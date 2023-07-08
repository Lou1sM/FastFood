from copy import copy,deepcopy
import numpy as np
from utils import direct_requires, transitive_closure, hours_minutes_seconds, randomly, split_respecting_brackets


def cont_form_word(w):
    if w in ['chop','mash','bake','boil','strain','fry','soak','peel','roast','place','add','heat','cook','leave','mix']:
        return w.rstrip('e')+'ing'
    else:
        return w

def cont_form(s):
    return ' '.join([cont_form_word(w) for w in s.split()])


class FastFooder():
    def __init__(self,known_foods,special_skills,synonyms,supplies):
        self.known_foods = known_foods
        self.skills = special_skills
        self.synonyms = synonyms
        self.supplies = supplies

        self.chop = {}
        self.mash = {}
        self.peel = {}
        self.soak = {}
        self.bake = {}
        self.boil = {}
        self.fry = {}
        self.roast = {}
        self.strain = {}

        self.requirees = []
        self.compressed_requirees = []
        self.can_make = []

        self.ghosts = []
        self.skills += self.ghosts

    def extend_food_classes(self):
        next_number = len(self.skills)
        known_foods_temp = deepcopy(self.known_foods)
        for i in range(5):
            if known_foods_temp == []:
                break
            known_foods1 = []
            for x in known_foods_temp:
                if x.chopable:
                    chopped_x = deepcopy(x)
                    chopped_x.chop()
                    self.chop[x.description()] = {'in': [x.description()], 'out': [chopped_x.description()], 'time': 120, 'f time': 0, 'direction': 'chop the ' + x.name, 'number': copy(next_number)}
                    next_number +=1
                    known_foods1.append(chopped_x)
                    done = False

                if type(x.boilable) is int:
                    boiled_x = deepcopy(x)
                    boiled_x.boil()
                    self.boil[x.description()] = {'number': next_number, 'in': [x.description(), 'boiling water'], 'out': [boiled_x.description() + ' in water'], 'time': x.boilable, 'f time': x.boilable-30, 'direction': 'add the ' + x.name + ' to the boiling water and cook for ' + str(hours_minutes_seconds(x.boilable)) + ', stirring occasionally'}
                    next_number +=1
                    self.strain[x.name] = {'number': next_number, 'in': [boiled_x.description() + ' in water'], 'out':[boiled_x.description()], 'time': 60, 'f time': 0, 'direction': 'strain the ' + x.name}
                    next_number +=1
                    done = False

                if type(x.fryable) is int:
                    fried_x = deepcopy(x)
                    fried_x.fry()
                    self.fry[x.description()] = {'number': next_number, 'in': [x.description()], 'out': [fried_x.description()], 'time': x.fryable, 'f time': x.fryable-30, 'direction': 'fry the ' + x.name}
                    next_number +=1
                    done = False

                if x.fryable:
                    fried_x = deepcopy(x)
                    fried_x.fry()
                    self.fry[x.description()] = {'number': next_number, 'in': [x.description()], 'out': [fried_x.description()], 'time': 500, 'f time': x.fryable-30, 'direction': 'fry the ' + x.name}
                    next_number +=1
                    done = False

                if x.peelable:
                    peeled_x = deepcopy(x)
                    peeled_x.peel()
                    self.peel[x.description()] = {'number': next_number, 'in': [x.description()], 'out': [peeled_x.description()], 'time': 300, 'direction': 'peel the ' + x.name, 'f time': 0}
                    next_number +=1
                    known_foods1.append(peeled_x)
                    done = False

                if x.mashable and (x.state == 'peeled' or x.peelable is False):
                    mashed_x = copy(x)
                    mashed_x.mash()
                    self.mash[x.description()] = {'number': next_number, 'in': [x.description()], 'out': [mashed_x.description()], 'time': 120, 'direction': 'mash the ' + x.name, 'f time': 0}
                    next_number +=1
                    known_foods1.append(mashed_x)
                    done = False
            self.known_foods += known_foods1
            known_foods_temp = known_foods1

    def update_skills(self):
        for x in self.chop:
            self.skills.append(self.chop[x])
        for x in self.mash:
            self.skills.append(self.mash[x])
        for x in self.bake:
            self.skills.append(self.bake[x])
        for x in self.boil:
            self.skills.append(self.boil[x])
        for x in self.strain:
            self.skills.append(self.strain[x])
        for x in self.fry:
            self.skills.append(self.fry[x])
        for x in self.soak:
            self.skills.append(self.soak[x])
        for x in self.peel:
            self.skills.append(self.peel[x])
        for x in self.roast:
            self.skills.append(self.roast[x])

    def update_can_make(self):
        self.can_make = []
        for x in self.skills:
            self.can_make = set(self.can_make).union(set(x['out']))

    def set_supplies(self,supplies):
        self.supplies = supplies

    def update_ghosts(self):
        next_number = len(self.skills)
        for x in self.synonyms:
            self.ghosts.append({'number': next_number, 'in': x[0], 'out': x[1], 'time': 0, 'f time': 0, 'direction': ''})
            next_number +=1
        self.skills += self.ghosts

    def determine_requires_relations(self):
        self.requirees = set([(a['number'],b['number']) for a in self.skills for b in self.skills if direct_requires(a,b)])
        self.base_requirees = transitive_closure(self.requirees)

    def prepare(self):
        self.extend_food_classes()
        self.update_skills()
        self.update_ghosts()
        self.determine_requires_relations()
        self.update_can_make()

    def concurrent_compression(self,l):
        """Temporally optimize a recipe plan within the given order of processes.
        Determines which processes it would be efficient to perform at the same
        time, and collapses them together into a 'derived process'

        Args:
            l - list of processes in a recipe
        """

        #temp_next = copy(next_number)
        temp_next = len(self.skills)
        modl = [item for item in deepcopy(l) if item['time'] > 0]
        size = len(modl)
        requirees = copy(self.base_requirees)
        #Reset requirees, otherwise there is a risk of 'cross contamination'
        #where a derived process is judged to have the dependencies of a
        #previous derived process (derived process from previous call of
        #temporal_compression) that had the same number.

        while True:
            #Adjoin all possible concurrent processes until nothing is
            #adjoined on a full iteration through `modl'.
            i = 2
            while True:
                if i > size:
                    #global requirees  #necessary for use of requirees in the 'best' function
                    self.compressed_requirees = requirees
                    return modl
                item = modl[-i]
                # For each processes, consider all following processes that it can
                #combine with(`eaten'). Iterate from end of list to allow derived
                #processes themselves to be eaten by another process that occurs
                #behind (before) them.
                if item['f time'] > 0:
                    concurrents = []
                    d = 0
                    while True:
                        #Iterate forward from item, adjoining it with any suitable steps.
                        d +=1
                        if -i + d >= 0:
                            i += 1
                            break
                        following_item = modl[-i+d]
                        if item['f time'] < following_item['time'] or self.dependent(item,following_item):
                            i += 1
                            break          # stops at first unsuitable step encountered
                        item['f time'] = item['f time'] - following_item['time'] + following_item['f time']
                        if following_item['time'] > 0:
                            concurrents.append(following_item)

                    if len(concurrents) > 0:
                        #Check if current item can be absorbed by some upcoming item,
                        #in which case the time savings would be greater by prioritising
                        #this larger absorption and removing anything from concurrents that
                        #may interfere.

                        if i <= len(modl):
                            going_to_be_absorbed = False
                            for index in range(0,len(modl)-i+2):
                                upcoming = modl[index]

                                time_ahead = 0
                                for index1 in range(index+1,len(modl)- i + 2):

                                    hypo_suc = modl[index1]
                                    time_ahead += hypo_suc['time']
                                    if time_ahead > upcoming['f time']:
                                        break
                                    if self.dependent(upcoming,hypo_suc):
                                        break
                                    if index1 == len(modl) - i + 1:
                                        going_to_be_absorbed = True
                                        break
                                if going_to_be_absorbed:
                                    for x in concurrents:
                                        if self.dependent(upcoming,x):
                                            concurrents.remove(x)
                                    break

                    if len(concurrents) > 0:
                        #Modify 'item' to become the new process by altering its
                        #dependencies, input, output and direction.

                        concurrent_instructions = [x['direction'] for x in concurrents]

                        for y in modl:
                            num = y['number']
                            if (item['number'],num) in requirees:
                                requirees.add((temp_next,num))

                            if (num,item['number']) in requirees:
                                requirees.add((num,temp_next))

                        for x in concurrents:
                            item['in'] += x['in']
                            item['out'] += x['out']
                            for y in modl:
                                num = y['number']
                                if (num,x['number']) in requirees:
                                    requirees.add((num,temp_next))
                                if (x['number'],num) in requirees:
                                    requirees.add((temp_next,num))
                            modl.remove(x)
                            size -= 1

                        item['number'] = copy(temp_next)
                        temp_next += 1
                        item['underlying direction'] = copy(item['direction'])
                        item['direction'] = 'while ' + cont_form(item['direction']) + '; ' + ', '.join(concurrent_instructions)
                else:
                    i += 1

    def get_ingredients(self,dish):
        """Work backwards from dish to supplies.

        Akin to a shift-reduce parser (though perhaps better
        called a shift-enlarge parser) and an ATP, by replacing
        the required elements with the inputs of a process for
        which they are in the output, and stores the processes
        used to do this, e.g. replaces 'rinsed beans' with 'beans'
        and saves the process 'rinse'.

        Args:
            dish - (str) name of dish to cook
        """
        lookingfor = [dish]
        action_list = []
        needed = []
        ingred_list = []
        while len(lookingfor)>0:
            #for food in lookingfor:
            food = lookingfor.pop()
            is_put_somewhere = False
            if food.startswith('mixture of'):
                new = split_respecting_brackets(food[11:],sep=';')
                lookingfor += [f.strip('()') for f in new]
                print(lookingfor)
                is_put_somewhere = True
                continue
            elif food in self.supplies:
                #lookingfor.remove(food)
                ingred_list.append(food)
                is_put_somewhere = True
                continue
            for x in self.skills:
                if food in x['out']:
                    #lookingfor.remove(food)
                    lookingfor = lookingfor + x['in']
                    action_list = [x] + action_list
                    is_put_somewhere = True
                    break
            #if food not in self.can_make:
            if not is_put_somewhere:
                needed.append(food)
                #is_put_somewhere = True
                #lookingfor.remove(food)
                continue

        if needed == []:
            #Return both ingredients reached and steps along the way
            return ingred_list, action_list
        else:
            print('Insufficient ingredients, you need: ')
            for x in needed:
                print(x)
            return

    def best(self,plan):
        """Test whether the recipe described in `plan' is temporally optimized."""
        if len(plan) == 1:
            return True

        for x in plan:
            if x['f time'] > 0:
                return False

        return True

    def quickest(self,l):
        """Find quickest of a list of plans.
        Args:
            l - a list of different plans and their times
        """
        choice = l[0]
        for x in l:
            if x[1] < choice[1]:
                choice = x
        return choice

    def get_time(self,plan):
        """Determine how long a recipe plan takes to execute.
        Args:
            plan - list of processes
        """
        time = 0
        for step in plan:
            time += step['time']
        return time

    def get_passives(self,l):
        """Determine which times during the carrying out of l are passive."""
        clock = 0
        passive_times = []
        for x in l:
            clock += x['time']
            if x['f time'] > 0:
                if 'underlying direction' in x:
                    passive_times.append(('from ' + str(clock - x['f time']) + ' to ' + str(clock) + ' while ' + cont_form(x['underlying direction']), x))
                else:
                    passive_times.append(('from ' + str(clock - x['f time']) + ' to ' + str(clock) + ' while ' + cont_form(x['direction']), x))
        return passive_times

    def free(self,a,l):
        """Determine whether a is independent in l, i.e. does not require
        some other element and so could occur first in an orderings.
        """
        for x in l:
            if (a['number'],x['number']) in self.requirees:
                return False
        return True

    def possible_next(self,a,l):
        """Return extension of `a' by each element of `l'. This is in the
        form of a list of lists,  each being 'a' with a possible next
        element appended.

        Args:
            l - list of processes
            a - sublist of l
        """
        possibles = []
        l1 = deepcopy(l)
        for x in a:
            l1.remove(x)
        for x in l1:
            if self.free(x,l1):
                possibles.append([x])
        possibles = [a + item for item in possibles]
        return possibles

    def find_all_paths(self,l):
        """Determin all permissable reorderings of `l' and return as a list of lists."""
        paths = self.possible_next([],l)
        for i in range(len(l)-1):
            paths1 = []
            for x in paths:
                up_next = self.possible_next(x,l)
                if len(up_next) > 0:
                    paths1.append(up_next)
            paths = [item for sublist in paths1 for item in sublist]
            if len(paths) > 10000:
                print(f'paths has got kinda long, cutting from {len(paths)} to 10000')
                idx = np.random.choice(len(paths),size=10000,replace=False)
                paths = [paths[i] for i in idx]
        return paths

    def find_quickest(self,recipe_plan):
        """Determine fastest way of executing the recipe described in `recipe_plan'.

        Define list of all permissable orderings of the processes in recipe_plan and
        determine fastest in each. This list is randomly shuffled to encourage more
        efficient searching.
        """
        paths = randomly(self.find_all_paths(recipe_plan))
        #choice = deepcopy(paths[0])
        #time = self.get_time(self.concurrent_compression(choice))
        #print('Number of permissable orderings: ' + str(len(paths)))
        best_time = np.inf
        best_choice = None
        #for i in range(min(len(paths),5000)):
        for choice in paths:

            #if self.best(self.concurrent_compression(choice)):
                #print(f'\nSolution found on ordering number {i}\n')
                #return self.concurrent_compression(choice), self.get_time(self.concurrent_compression(choice))

            #choice = deepcopy(paths[i])
            compressed  = self.concurrent_compression(choice)
            if self.best(compressed):
                print(f'\nSolution found early')
                return compressed, self.get_time(compressed)

            time = self.get_time(compressed)
            if time < 1500:
                breakpoint()
            if time < best_time:
                best_choice = choice
                best_time = time
        return self.concurrent_compression(best_choice), best_time

    def dependent(self,a,b):
      return (a['number'],b['number']) in self.requirees or (b['number'], a['number']) in self.requirees

    def cook(self,dish):
        """Take a single argument which is a description of a dish.
        If ingredients are not all in dish, prints the additional ingredients
        required; otherwise  returns the number of orderings considered,
        whether a definite best was found (currently answer is ususally no,
        see 'best' above), the time taken for the solution reached, the
        ingredients required to make the dish, the instructions and the time
        at which to perform each instruction, and the times during the cooking
        at which the person cooking will be passive.

        Args:
            dish (str): description of dish
        """

        if self.get_ingredients(dish) is None:
            return
        ingred_list, action_list_ = self.get_ingredients(dish)
        action_list = [item for item in action_list_ if item['time'] > 0]
        plan = self.find_quickest(action_list)[0]
        time = self.get_time(plan)
        passives = self.get_passives(plan)

        print(f'INPUT:\n{dish}\n')
        print(f'OUTPUT:\n')
        print('Time: ' + hours_minutes_seconds(time))
        print('Ingredients: ')
        for x in ingred_list:
            if not x == 'tap water':
                print(x)
        print('')
        print('Instructions:')
        time_point = 0
        for x in plan:
            print(hours_minutes_seconds(time_point)+':', x['direction'])
            time_point += x['time']
        print('')
        if not passives == []:
            print('Passive: ')
        for x in passives:
            print(x[0])
