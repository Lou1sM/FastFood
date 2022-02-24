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

from food_classes import Vegetable, Herb, Carb, Nut, Food
from copy import copy,deepcopy
from utils import direct_requires, transitive_closure, hours_minutes_seconds, randomly
from fast_food import FastFooder


#Define the objects used in this programme. Note these are simply
#shortcuts for defining processes and are not equivalent to ingredients

#List of processes arising from object definitions.

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


#vegetables = []



#List of 'specialised', hard-coded processes.

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


synonyms = [(['mashed avocado'],['guacamole']),(['fried chopped potato'],['chips']),(['fried chopped peeled sweet potato'],['sweet potato fries'])]
for x in foods:
    for y in foods:
        if type(x) is Vegetable and type(y) is Vegetable and not x.name == y.name and x.state == 'chopped' and y.state == 'chopped':
            synonyms.append(([x.description(),y.description()],['chopped vegetables']))

supplies = ['raw carrot','tinned beans','bread','avocado','tap water','lentils','coconut milk','raw peppers','olive oil','raw broccoli','pasta','happy pear tomato pesto', 'pine nuts','raw cashews','whole lemon','apple cider vinegar', 'dijon mustard', 'salt','pepper','nutritional yeast','raw garlic','tinned tomatoes', 'fresh basil', 'raw onion','lasagne sheets','soaked cashews','chopped garlic','raw potato','raw sweet potato','rice']


ff = FastFooder(foods=foods,special_skills=skills,supplies=supplies,synonyms=synonyms)
ff.prepare()
ff.extend_food_classes()

ff.cook('vegetable dahl')
