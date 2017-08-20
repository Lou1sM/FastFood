""" 

The following programme is an attempt to model cooking recipes in a way that is easy to work with and facillitates useful computation of temporal properties. The first half of the programme is devoted to defining the terms used in the recipe. The basic idea is to begin with descriptions, from descriptions define processes, and from processes define objects. Descriptions are strings describing either an ingredient, a dish or a partially made dish e.g. 'fried vegetables', processes are dictionaries that contain the input and output descriptions, their duration, and some other properties which will be discussed below. Objects are essentially shortcuts for defining many similar processes in one go. They are python objects of the defined class 'Food', which are intialised as having a string describing the object, a string describing its state, and several booleans determining which object functions can be applied to it. For every such object function, a process is created whose input is the given object and whose output is the given object with the given function applied to it. Ingredients and dishes are not objects, but descriptions; objects are not entities in the world but a set of order pairs of descriptions. For example the object 'carrot' is not something that is used in a recipe, but is a tool for considering/generating all the processes whose input and output strings are some variant of the string 'carrot'. 

The second part of the programme uses this structure to compute information about the recipe for a particular dish: the ingredients needed, the directions to be followed, the time taken, and the passive times when no action is required e.g. when the lentils are boiling. The was the intial intention was simply to make a division between active and passive times, but of course passive times can often be filled with something useful, e.g. chopping the peppers while the lentils are boiling, and this is in fact a desired quality as it reduces the overall cooking time. Thus, another question presented itself: how can the steps in a given recipe be most efficiently fitted into each other. The bulk of the following code is concerned with this problem, and a solution is presented based on two main algorithms. The concurrent_compression function is applied to a plan (list of processes); it iterates through the plan and collapses suitable neighbouring processes into one super-processes (the details of what counts as suitable are discussed below, but the most obvious criterion is that there be passive time in one of the processes). Which processes end up being lumped together (the shorthand used below is that the larger passive process 'eats' the smaller) is dependent on the order in the input plan, so a second algorithm is used to determine all permissable orderings of a given list of processes. Of course not every order is permissable, it is impossible to slice the toast before toasting the bread, and in fact defining this dependency relation between the relevant processes turns out to be the most delicate part of this second algorithm. The result is that every permissable order can be considered, run through concurrent_compression, and then the one with least total time can be returned. 


While the code runs smoothly in executing the above process, there are several areas that could do with improvement or expansion. Specifically there are three large issues, and two smaller ones. I will mention the large issues first.
The most notable omission is that of quantitiy, a notion which, as it stands, is entirely absent. This has two notable effects, firstly the ingredients list is unclear and contains multiplicities when the same foodstuff is used in two different parts of the recipe, secondly the times given for each process cannot consider the amount of the input and output, which is obviously relevant. 
The second problem is the function used to determine whether an quickest order has been reached--there are normally multiple quickest orderings. The difficulty can best be observed by considering the recipe plans possible_false_negative and possible_false_positive below, so far attempts have been unsuccessful at judging the former to be an quickest order and the latter not to be. The false negatives are preferred because they do not result in a wrong answer, but this decreases efficiency by not allowing the programme to halt at the earliest possible time. 
The third substantial problem is the generation of the list of all possible orderings. The current method generates every element simultaneously rather than each at a time, but if the latter could be acheived then the searching function could consider only a portion of the total and, with the right search method, still have a high probability of finding a correct solution. The result of the second and third problems is that the programme stall for recipes longer than 11 steps. The number of permissable orders is bounded only by the factorial of recipe length, and with the current set up the programme must generate this whole list and then iterate through it. 
The other two problems are termed small, not so much because they have obvious solutions but because they interfere minimally with the central aspect of the programme. The first is that there is no allowance made for different ways of making the same thing (not different orderings but different ingredients and processes). Currently, the programme programme simply uses the first it encounters. The second is that the output is not a well-formed discourse, and sometimes contains non-grammatical sentences. The difficulty of such a solution would depend on the strictness of the standards by which the discourse is judged to be well-formed. 

This programme utilises a novel representation of cooking terms, and is able to use these representations to derive practical information about the recipe for a given dish. There is large potential for improvement, by solving the above mentioned problems and by scaling the aspects of the programme. 

"""

from random import randint
from random import shuffle
from copy import deepcopy
from copy import copy 

from copy import copy


class Food(object): 
  
  #certain objects are classified as Foods to enable a general definition of all processes that can be done to them, e.g. chop carrots, boil carrots, peel carrots etc 
  
  
  def __init__(self,name,state,chopable,mashable,peelable,soakable,bakeable,boilable,fryable,roastable):
    self.name = name
    self.state = state 
    self.fryable = fryable
    self.chopable = chopable
    self.soakable = soakable
    self.boilable = boilable
    self.peelable = peelable
    self.mashable = mashable
    self.bakeable = bakeable
    self.roastable = roastable
    
  def get_info(self):
    return self.amount + '\n ' + self.state + '\n' + self.name 
    
  #the following class functions essentially allow an object to be considered in various forms: raw broccoli, chopped broccoli etc, forms which differ only slightly
    
  def chop(self):
    self.chopable = False
    self.peelable = False
    if self.state == 'raw' or 'soaked' or 'whole' or '':
      self.state = 'chopped' 
    else:
      self.state = 'chopped ' + self.state
    
      
  def mash(self):
    self.chopable = False
    self.mashable = False
    self.soakable = False
    self.boilable = False
    if self.state == 'raw' or 'soaked' or 'whole' or '' or 'peeled':
      self.state = 'mashed' 
    else:
      self.state = 'mashed ' + self.state 
    
  def peel(self):
    self.peelable = False
    if self.state == 'raw' or 'soaked' or 'whole' or '':
      self.state = 'peeled' 
    else:
      self.state = 'peeled ' + self.state
    
  def soak(self):
    if self.state == 'raw' or 'soaked' or 'whole' or '':
      self.state = 'soaked' 
    else:
      self.state = 'soaked ' + self.state
      
      
  def bake(self):
    self.chopable = False
    self.mashable = False
    self.peelable = False
    self.soakable = False
    self.boilable = False
    if self.state == 'raw' or 'soaked' or 'whole' or '':
      self.state = 'baked' 
    else:
      self.state = 'baked ' + self.state
    
  def boil(self):
    self.mashable = True
    self.boilable = False
    if self.state == 'raw' or 'soaked' or '':
      self.state = 'boiled'
    else:
      self.state = 'boiled ' + self.state
    
    
  def fry(self):
    self.soakable = False 
    self.boilable = False
    self.fryable = False
    if self.state == 'raw' or self.state == 'soaked' or self.state == 'whole' or self.state == '':
      self.state = 'fried' 
    else:
      self.state = 'fried ' + self.state
    
  def roast(self):
    self.chopable = False
    self.mashable = False
    self.peelable = False
    self.soakable = False
    self.boilable = False
    self.roastable = False
    if self.state == 'raw' or 'soaked' or 'whole' or '':
      self.state = 'roasted ' 
    else:
      self.state = 'roasted ' + self.state
    
    
    
  def description(self): 
    if self.state == '':
      return self.state + self.name
    else:
      return self.state + ' ' + self.name
    
    
# what follows defines subclasses of Foods which agree on many properties, the properties on which they may not agree  are left open to be defined for each object
    
class Vegetable(Food):
  
  def __init__(self,name,peelable,boilable):
    self.name = name
    self.state = 'raw'
    self.chopable = True
    self.mashable = False
    self.peelable = peelable
    self.soakable = False
    self.bakeable = True
    self.boilable = boilable
    self.fryable = False
    self.roastable = True
    
  def chop(self):
    self.chopable = False
    self.peelable = False 
    if self.state == 'peeled':
      self.state = 'chopped ' + self.state
    else:
      self.state = 'chopped' 
    if type(self.boilable) is int:
      self.boilable -= 300
    self.fryable = True 
    self.roastable = True 
    
    
class Herb(Food):
  
  def __init__(self,name):
    self.name = name 
    self.state = 'fresh' 
    self.fryable = False
    self.chopable = True
    self.soakable = False
    self.boilable = False
    self.peelable = False
    self.mashable = False
    self.bakeable = False
    self.roastable = False
    
class Carb(Food):
  
  def __init__(self,name,boilable):
    self.name = name 
    self.state = '' 
    self.fryable = False
    self.chopable = False
    self.soakable = False
    self.boilable = boilable
    self.peelable = False
    self.mashable = False
    self.bakeable = False
    self.roastable = False
    
    
class Nut(Food):
  
  def __init__(self,name):
    self.name = name 
    self.state = 'whole' 
    self.fryable = False
    self.chopable = True
    self.soakable = True
    self.boilable = False
    self.peelable = False
    self.mashable = False
    self.bakeable = False
    self.roastable = True
                                
                                
  # a definition of the objects used in this programme, note these are simply shortcuts for defining processes and are not equivalent to ingredients 
  
  #chop,mash,peel,soak,bake,boil,fry,roast
    
carrot = Vegetable('carrot',True,600)
bean = Food('beans','dried',False,False,False,True,False,False,False,False)
broccoli = Vegetable('broccoli',False,480)
peppers = Vegetable('peppers',True,120)
cauliflower = Vegetable('cauliflower',False,480)
asparagus = Vegetable('asparagus',False,600)
onion= Vegetable('onion', False,1200)
tomato = Vegetable('tomato',True,False)
potato = Vegetable('potato',True,1800)
vegetables = Vegetable('vegetables',False,600)
sweet_potato = Vegetable('sweet potato',True,1500)
garlic = Food('garlic','raw',True,True,False,False,False,False,False,True)
rosemary = Herb('rosemary')
basil = Herb('basil')
parsley = Herb('parsley')
thyme = Herb('thyme')
noodles = Carb('noodles',300)
pasta = Carb('pasta',600)
quinoa = Carb('quinoa',900)
rice = Carb('rice',1500)
lentils = Carb('lentils',2700)
cashew = Nut('cashews')
almond = Nut('almond')
pecan = Nut('pecan')
walnut = Nut('walnut')
avocado = Food('avocado','',False,True,True,False,False,False,False,False)




foods = [carrot,bean,broccoli,peppers,cauliflower,asparagus,onion,tomato,potato,rosemary,basil,parsley,thyme,noodles,rice,pasta,lentils,quinoa,garlic,avocado,sweet_potato]



vegetables = []



chop = {}
mash = {}
peel = {}
soak = {}
bake = {}
boil = {}
fry = {}
roast = {}
strain = {}


# the list of 'specialised' processes is defined first, the processes arising from object definitions are appended later


rinse = {'number': 1, 'in': ['tinned beans'], 'out': ['rinsed beans'], 'time': 60, 'direction': 'rinse the beans','f time': 0}
serve_salad = {'number': 2, 'in': ['chopped carrot', 'rinsed beans'],'out': ['bean salad'],'time': 30,'direction': 'add the carrots and beans and serve','f time': 0}

toast = {'number': 4, 'in': ['bread'],'out': ['toast'],'time': 175,'direction': 'toast bread in toaster','f time': 165}
soldiers = {'number': 5, 'in': ['toast'],'out': ['strips of toast'],'time': 30, 'direction': 'slice toast into strips','f time': 0}
serve_guac = {'number': 6, 'in': ['strips of toast','guacamole'],'out': ['guac and toast'], 'time': 15, 'direction' : 'serve the guac together with the toast strips','f time': 0}
bring_to_boil = {'number': 7, 'in': ['tap water'], 'out': ['boiling water'], 'time': 300, 'direction': 'place water in pot and heat on cooker', 'f time': 270}
fry_broc_and_pep = {'number': 8, 'in': ['chopped broccoli', 'chopped peppers', 'olive oil',], 'out': ['sauteed vegetables'], 'time': 420, 'direction': 'heat olive oil in pan and add chopped vegetables, fry until soft', 'f time': 360}
mix_dahl = {'number': 9, 'in': ['sauteed vegetables', 'boiled lentils', 'coconut milk',], 'out': ['vegetable dahl'], 'time': 120, 'direction': 'add the sauteed vegetables and coconut milk to the lentils and stir', 'f time': 0}
mix_special_pasta = {'number': 10, 'in': ['sauteed vegetables', 'boiled pasta', 'pine nuts', 'happy pear tomato pesto'], 'out': ['special pasta'], 'time': 60, 'direction': 'add the vegetables, tomato pesto and pine nuts to the pot containing the strained pasta and stir', 'f time': 0}
mix_cashew_cheese = {'number': 11, 'in': ['soaked cashews', 'nutritional yeast', 'lemon juice', 'chopped garlic', 'apple cider vinegar', 'dijon mustard', 'salt', 'pepper'], 'out': ['vegan cashew cheese'], 'time': 600, 'direction': 'mix all ingredients for cashew cheese in food processor', 'f time': 0}
soak_cashews = {'number': 12, 'in': ['raw cashews', 'tap water'], 'out': ['soaked cashews'], 'time': 10800, 'direction': 'leave cashews in bowl of water for 2 hours', 'f time': 10750}
squeeze_lemon = {'number': 13, 'in': ['whole lemon'], 'out': ['lemon juice', 'dry lemon'], 'time': 60, 'direction': 'squeeze the lemon', 'f time': 0}
fry_onion_and_garlic = {'number': 14, 'in': ['chopped onion', 'chopped garlic'], 'out': ['sauteed onion and garlic'], 'time': 120, 'direction': 'fry onion and garlic on medium heat, not letting garlic burn', 'f time': 0}
fry_marinara = {'number': 15, 'in': ['sauteed onion and garlic', 'tinned tomatoes', 'salt', 'pepper', 'chopped basil'], 'out': ['marinara sauce'], 'time': 630, 'direction': 'add the tinned tomatoes, salt, pepper and basil to the onion and garlic and simmer for 10 min', 'f time': 600} 
assemble_lasagne = {'number': 16, 'in': ['sauteed vegetables', 'marinara sauce', 'lasagne sheets', 'vegan cashew cheese'], 'out': ['uncooked vegan lasagne'], 'time': 300, 'direction': 'in large baking dish add layer of vegetables, layer of sauce, layer of cheese, until all three have been used up', 'f time': 0} 
bake_lasagne = {'number': 17, 'in': ['uncooked vegan lasagne'], 'out': ['vegan lasagne'], 'time': 2400, 'direction': 'bake lasagne for 40 min', 'f time': 2330}


skills = [bring_to_boil,mix_dahl,rinse,serve_salad,toast,soldiers,serve_guac,fry_broc_and_pep,mix_special_pasta, mix_cashew_cheese,soak_cashews,squeeze_lemon,fry_onion_and_garlic,fry_marinara, assemble_lasagne,bake_lasagne]





def hours_minutes_seconds(t):
  # t is an amount of time given in seconds, returns the same amount of time given in hrs, mins and secs  
  secondcount = t % 60
  minutecount = (t % 3600 - secondcount)/60
  hourcount = (t - secondcount - (minutecount *60))/3600
  if t == 0:
    return 0 
  if hourcount == 0:
    hours = ''
  elif hourcount == 1:
    hours = str(hourcount) + 'hr'
  else:
    hours = str(hourcount) + 'hrs'
    
  if minutecount == 1:
    minutes = str(minutecount) + 'min'
  else:
    minutes = str(minutecount) + 'mins'
    
  if secondcount == 0:
    seconds = ''
  elif secondcount == 1:
    seconds = str(secondcount) + 'sec'
  else:
    seconds = str(secondcount) + 'secs'
  return hours + minutes + seconds 
  
  

next_number = 18
foods_temp = deepcopy(foods)
for i in range(5):
  

  if foods_temp == []:
    break
  foods1 = []
  for x in foods_temp:
    if x.chopable == True:
      chopped_x = deepcopy(x)
      chopped_x.chop()
      chop[x.description()] = {'in': [x.description()], 'out': [chopped_x.description()], 'time': 120, 'f time': 0, 'direction': 'chop the ' + x.name, 'number': copy(next_number)}
      next_number +=1
      foods1.append(chopped_x)
      done = False

    if type(x.boilable) is int:
      boiled_x = deepcopy(x)
      boiled_x.boil()
      boil[x.description()] = {'number': next_number, 'in': [x.description(), 'boiling water'], 'out': [boiled_x.description() + ' in water'], 'time': x.boilable, 'f time': x.boilable-30, 'direction': 'add the ' + x.name + ' to the boiling water and cook for ' + str(hours_minutes_seconds(x.boilable)) + ', stirring occasionally'}
      next_number +=1
      strain[x.name] = {'number': next_number, 'in': [boiled_x.description() + ' in water'], 'out':[boiled_x.description()], 'time': 60, 'f time': 0, 'direction': 'strain the ' + x.name}
      next_number +=1
      done = False
    
    if type(x.fryable) is int:
      fried_x = deepcopy(x)
      fried_x.fry()
      fry[x.description()] = {'number': next_number, 'in': [x.description()], 'out': [fried_x.description()], 'time': x.fryable, 'f time': x.fryable-30, 'direction': 'fry the ' + x.name}
      next_number +=1
      done = False
      
    if x.fryable == True:
      fried_x = deepcopy(x)
      fried_x.fry()
      fry[x.description()] = {'number': next_number, 'in': [x.description()], 'out': [fried_x.description()], 'time': 500, 'f time': x.fryable-30, 'direction': 'fry the ' + x.name}
      next_number +=1
      done = False
    
    if x.peelable == True:
      peeled_x = deepcopy(x)
      peeled_x.peel()
      peel[x.description()] = {'number': next_number, 'in': [x.description()], 'out': [peeled_x.description()], 'time': 300, 'direction': 'peel the ' + x.name, 'f time': 0}
      next_number +=1
      foods1.append(peeled_x)
      done = False
    
  if x.mashable == True and (x.state == 'peeled' or x.peelable == False):
    mashed_x = copy(x)
    mashed_x.mash()
    mash[x.description()] = {'number': next_number, 'in': [x.description()], 'out': [mashed_x.description()], 'time': 120, 'direction': 'mash the ' + x.name, 'f time': 0}
    next_number +=1
    foods1.append(mashed_x)
    done = False 
  foods += foods1  
  foods_temp = foods1  

  

  # synoyms are managed by 'ghost' processes which convert between synonymous terms, contain empty direction and 0 time     
synonyms = []
   
synonyms = [(['mashed avocado'],['guacamole']),(['fried chopped potato'],['chips']),(['fried chopped peeled sweet potato'],['sweet potato fries'])]  
for x in foods:
  for y in foods:
    if type(x) is Vegetable and type(y) is Vegetable and not x.name == y.name and x.state == 'chopped' and y.state == 'chopped':
      synonyms.append(([x.description(),y.description()],['chopped vegetables']))
      
# the above allows the automatic generation of 'chopped vegetables' for example, but requires some tweaking to allow for more than two vegetable types to count as chopped vegetables, e.g. broccoli, carrot and onion 
# the conversion is made only in the chopped state because it is felt that, practically speaking, this is the most likely stage at which one would begin treating many vegetables as a single ingredient/description, however an increase in generality would still be a worthwhile step 
    

ghost = []

for x in synonyms:
  ghost.append({'number': next_number, 'in': x[0], 'out': x[1], 'time': 0, 'f time': 0, 'direction': ''})
  next_number +=1 
skills += ghost

# the following appends the processes arising from object definitions

for x in chop:
  skills.append(chop[x])
for x in mash:
  skills.append(mash[x])
for x in bake:
  skills.append(bake[x])
for x in boil:
  skills.append(boil[x])
for x in strain:
  skills.append(strain[x])
for x in fry:
  skills.append(fry[x])
for x in soak:
  skills.append(soak[x])
for x in peel:
  skills.append(peel[x])
for x in roast:
  skills.append(roast[x])



supplies = ['raw carrot','tinned beans','bread','avocado','tap water','lentils','coconut milk','raw peppers','olive oil','raw broccoli','pasta','happy pear tomato pesto', 'pine nuts','raw cashews','whole lemon','apple cider vinegar', 'dijon mustard', 'salt','pepper','nutritional yeast','raw garlic','tinned tomatoes', 'fresh basil', 'raw onion','lasagne sheets','soaked cashews','chopped garlic','raw potato','raw sweet potato','rice']



#  the following 6 functions enable a plan of a recipe to be encoded by a single integer, this is a sort of work around of the fact that, in python, lists are unhashable, it allows python to perform certain actions that cannot be performed on the alternative form of a plan (a list of dictionaries)--while these functions are not used in the current version of the code, they were helpful in previous versions and are included in case they prove useful in the future 


def list_of_primes(i):
  # returns a list of the first i primes
  if i == 0:
    return []
    
  else:
    l = [2]
    place = l[-1] + 1
    
    while True:
      if len(l) == i:
        return l 
      for item in l:
        if item**2 > place:
          l.append(place)
          place += 1 
          break
        if place%item == 0:
          place += 1 
          break
        
        
def g_num(l):
  # transforms a list of numbers into a single number through a technique similar to part of that of Goedel Numbering 
  g = list_of_primes(len(l))
  g_num = 1 
  for i in range(len(l)):
    g_num *= g[i]**l[i]
  return g_num  
  
def recipe_num_list(plan):
  # relates each plan to a unique list of integers 
  l = []
  for x in plan:
    l.append(x['number'])
  return l 
  
def recipe_num(plan):
  # relates each plan to a unique integer
  l = recipe_num_list(plan)
  return g_num(l)
  
  
def plan_from_num(n):
  # the inverse function of recipe_num, relates each integer to a unique list of processes, of course the majority of these lists will not be meaningful
  g = list_of_primes(20)
  plan_num = []
  for x in g:
    if n == 1:
      break

    times = 0
    while True:
      if n%x == 0:

        times +=1 
        n = n/x 

      else:

        plan_num.append(times)

        break
  plan = []
  for num in plan_num:
    plan.append(find_number(num))
    
  return plan 

  
def find_number(a):
  # returns the unique process with number equal to a 
  for x in skills:
    if x['number'] == a:
      return x
      





can_make = []


for x in boil:
  if not type(boil[x]) is dict:
    print boil[x] 
   

# the set of all (parts of) dishes that are recognised by the current programme--this is not equivalent to the dishes that can be made with the given ingredients however, additional ingredients may be required
    
for x in skills:
  can_make = set(can_make).union(set(x['out']))
  

# the following functions build up a definition of the relation that holds between two processes when one requires (cannot be performed before) the other--as the processes are dictionaries and so unhashable, they are represented in the set 'requirees' by a unique identifying number, a number which has the dictionary key 'number'

def direct_requires(a,b):
  return not set(a['in']).intersection(set(b['out'])) == set([])
  
  
def direct_dependent(a,b):
  return direct_requires(a,b) or direct_requires(b,a)


direct_requirees = set([(a['number'],b['number']) for a in skills for b in skills if direct_requires(a,b)])


def transitive_closure(s):
  closure = set(s)
  while True:
    new_elements = set((a,b) for (a,x) in closure for (z,b) in s if x == z)
    new_closure = closure | new_elements
    if new_closure == closure:
      break
    closure = new_closure
  return closure
    

base_requirees = transitive_closure(direct_requirees)

requirees = copy(direct_requirees)

def dependent(a,b):
  return (a['number'],b['number']) in requirees or (b['number'], a['number']) in requirees



def best(plan):
  
  if len(plan) == 1:
    return True 
    
  for x in plan:
    if x['f time'] >  0:
      return False
  
  return True 
    
   
  


  
    # takes a plan as argument and returns the quickest way this plan could be performed without altering the order of processes, i.e. determines which processes it would be efficient to perform at the same time, and collapses them together into a 'derived process' 


def concurrent_compression(l):

  temp_next = copy(next_number)
  modl = [item for item in deepcopy(l) if item['time'] > 0]
  size = len(modl)
  count = 0 
  requirees = copy(base_requirees)    
  # it is necessary to reset the requirees set on every call of the current function, otherwise there is a risk of 'cross contamination' where a derived process is judged to have the dependencies of a previous derived process (derived process from previous call of temporal_compression) that had the same number  
  
  while True:
    
    # adjoin all possible concurrent processes until nothing is adjoined on a full iteration through modl 
    i = 2
    while True:
      if i > size:
        global requirees  #necessary for use of requirees in the 'best' function 
        return modl
      item = modl[-i]     
      # begins from last in list, considering all items in front of it that can be adjoined (eaten), this direction is taken to allow derived processes themselves to be eaten by another process that occurs behind (before) them 
      if item['f time'] > 0:
        
        concurrents = []
        d = 0
        while True:   #moves forward from item, adjoining it with any suitable steps 
          d +=1 
          if -i + d >= 0:
            i += 1
            break
          following_item = modl[-i+d]
          if item['f time'] < following_item['time'] or dependent(item,following_item):
            i += 1 
            break          # stops at first unsuitable step encountered
          item['f time'] = item['f time'] - following_item['time'] + following_item['f time']
          if following_item['time'] > 0:
            concurrents.append(following_item)
          
          
          
        if not concurrents == []:

              # checks if current item can be absorbed by some upcoming item, in which case the time savings would be greater by prioritising this larger absorption and removing anything from concurrents that may interfere
          
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
                if dependent(upcoming,hypo_suc):
                  break
                if index1 == len(modl) - i + 1:
                  going_to_be_absorbed = True
                  break 
              if going_to_be_absorbed == True:
                for x in concurrents:
                  if dependent(upcoming,x):
                    concurrents.remove(x)
                break
              
        if not concurrents == []:    
          #modifies 'item' to become the new process by altering its dependencies, input, output and direction 
          
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
          item['direction'] = 'while ' + item['direction'] + ', ' + ', '.join(concurrent_instructions)

            
            
      else:
        i += 1 
   
  




 



 

def quickest(l): # l is a list of different plans and their times
  choice = l[0]
  for x in l:
    if x[1] < choice[1]:
      choice = x

  return choice  





def get_ingredients(dish):  
  # akin to a shift-reduce parser (though perhaps better called a shift-enlarge parser) and an ATP,works backwards from dish to supplies by replacing the required elements with the inputs of a process for which they are in the output, and stores the processes used to do this, e.g. replaces 'rinsed beans' with 'beans' and saves the process 'rinse'
    
  lookingfor = [dish]
  action_list = []
  needed = []
  ingred_list = []
  while True:
    for food in lookingfor:
      if food in supplies:
        lookingfor.remove(food)
        ingred_list.append(food)
        continue
      
      if not food in can_make:
        needed.append(food)
        lookingfor.remove(food)
        continue
      for x in skills:
        if food in x['out']:
          lookingfor.remove(food)
          lookingfor = lookingfor + x['in'] 
          action_list = [x] + action_list
          break
    if lookingfor == []:
      if needed == []:
        return ingred_list, action_list   # returns both ingredients reached and steps along the way 
      else:
        print 'Insufficient ingredients, you need: '
        for x in needed:
          print x
        return
  


def randomly(seq):
  shuffled = seq
  shuffle(shuffled)
  return shuffled




  #determines how long a plan takes to execute
  
def get_time(plan):

  time = 0 
  for step in plan:
    time += step['time']
  return time
  

  #determines which times during the carrying out of l are passive 
  
def get_passives(l):
  
  clock = 0 
  passive_times = []
  for x in l:
    clock += x['time']


    print str(clock - x['f time']) + ' to ' + str(clock)
    if x['f time'] > 0:
      if 'underlying direction' in x:
        passive_times.append(('from ' + str(clock - x['f time']) + ' to ' + str(clock) + ' while ' + x['underlying direction'], x))
      else:
        passive_times.append(('from ' + str(clock - x['f time']) + ' to ' + str(clock) + ' while ' + x['direction'], x))
    
  return passive_times
  
  
# the following 3 functions allow consideration of all permissable orderings of a given list of processes, the function find_all_paths takes a single argument l, where l is a plan for making a dish, and returns a list containing all permissable reorderings of this plan (reorderings that respect the requires relation)
  


def free(a,l):
  # determines whether a is independent in l, i.e. does not require some other element and so could occur first in an orderings
  for x in l:
    if (a['number'],x['number']) in requirees:
      return False
  return True 
  
def possible_next(a,l):     
    #'a' is a sublist of l, returns a list of lists, each being 'a' with a possible next element appended
  possibles = []
  l1 = deepcopy(l) 
  for x in a:
    l1.remove(x)
  for x in l1:
    if free(x,l1):
      possibles.append([x])
  possibles = [a + item for item in possibles]
  return possibles 
        
def find_all_paths(l):
  # l is plan, returns a list of all permissable reorderings of l 
  paths = possible_next([],l)
  for i in range(len(l)-1):
    paths1 = []
    for x in paths:
      up_next = possible_next(x,l)
      if len(up_next) > 0:
        paths1.append(up_next)
    
    paths = [item for sublist in paths1 for item in sublist]
  
  return paths 
  
  
def find_quickest(l):

  paths = randomly(find_all_paths(l)) 
  
  # paths is a list of all permissable orderings of the processes in l, it is randomly shuffled to encourage more efficient searching 
  
  choice = deepcopy(paths[0])
  time = get_time(concurrent_compression(choice))
  print 'Number of permissable orderings: ' + str(len(paths))
  for i in range(1,min(len(paths),5000)):

    if best(concurrent_compression(choice)):
      print ''
      print 'Solution found on ordering number ' + str(i) 
      print ''
      return concurrent_compression(choice), get_time(concurrent_compression(choice))
      
    choice1 = deepcopy(paths[i])
    time1 = get_time(concurrent_compression(choice1))
    if time1 < time:
      choice = choice1
      time = time1

  print 'no definite best found'
  print 'steps'
  print len(choice)
  return concurrent_compression(choice), time

  
  



def cook(dish):
  # takes a single argument which is a description of a dish--if ingredients are not all in dish, prints the additional ingredients required; otherwise  returns the number of orderings considered, whether a definite best was found (currently answer is ususally no, see 'best' above), the time taken for the solution reached, the ingredients required to make the dish, the instructions and the time at which to perform each instruction, and the times during the cooking at which the person cooking will be passive  
  if get_ingredients(dish) == None:
    return 
  
  ingred_list  = get_ingredients(dish)[0]
  action_list = [item for item in get_ingredients(dish)[1] if item['time'] > 0]
 
  

  plan = find_quickest(action_list)[0]
  time = get_time(plan)
  passives = get_passives(plan)
   
  
  for x in plan:
    print 888
    print x['f time']
 
  print 'Time: ' + hours_minutes_seconds(time)
  print 'Ingredients: '
  for x in ingred_list:
    if not x == 'tap water':
      print x 
  print ''
  print 'Instructions:'
  time_point = 0 
  for x in plan:
    print hours_minutes_seconds(time_point), x['direction'] 
    time_point += x['time']
  print ''
  if not passives == []:
    print 'Passive: '
  for x in passives:
    print x[0] 
    


print len(skills)

cook('special pasta')
    
possible_false_negative = [fry_broc_and_pep, chop['fresh basil'], chop['raw onion'], fry_onion_and_garlic, squeeze_lemon, fry_marinara, mix_cashew_cheese, assemble_lasagne, bake_lasagne]


possible_false_positive = [chop['raw onion'], fry_onion_and_garlic, chop['fresh basil'], chop['raw broccoli'], fry_marinara, chop['raw peppers'], fry_broc_and_pep, squeeze_lemon, mix_cashew_cheese, assemble_lasagne, bake_lasagne]

other_option = [bring_to_boil, chop['raw broccoli'], chop['raw peppers'], boil['lentils'], fry_broc_and_pep, strain['lentils'], mix_dahl]




#current problem is that passive time on boli lentils is too large, 2550 instead of 2250, when cooking vegetable dahl

#I have removed the transitive closure of requires because I realised it is unnecessary, can never affect a change