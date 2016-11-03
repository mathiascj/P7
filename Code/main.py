from module import Module, Configuration
from verifytaAPI import run_verifyta, get_best_cost
from xml_generator import generate_xml, generate_query
from genetic_algorithm import genetic_algorithm
from random import randint, choice, random, shuffle
from bisect import bisect_left
from itertools import combinations
from bisect import bisect_left

def get_island(start_module, configuration):
    """
    A Fuglsang inspired method <3
    For a given starting module we return a list of all modules connected to this set
    :param start_module: Id of the module from which the search starts
    :param configuration: Factory configuration as a list of sets.
    :return: List of all modules connected to the starting module
    """

    reached_modules = [start_module]
    flag = False

    # Continues building the list until it can't be expanded no more
    while not flag:
        reached_modules_copy = reached_modules.copy()

        # Add all modules, that reached modules connect to
        for module in reached_modules_copy:
            reached_modules = reached_modules + [x for x in configuration.keys()
                                             if x in configuration[module]
                                             and x not in reached_modules]

        # Add all modules that connect to reached modules
        for module in configuration.keys():
           if module not in reached_modules:
             for reached_module in reached_modules_copy:
               if reached_module in configuration[module]:
                 reached_modules.append(module)

        # When the last iteration added no new modules exit loop
        if len(reached_modules) == len(reached_modules_copy):
            flag = True

    return reached_modules


def weighted_random_select(select_list):
    """
    Does a weighted select on a list of element.
    The larger the element, the less chance it has of being chosen
    :param select_list: List of elements to select from
    :return: Selected element from list
    """
    total = 0
    cum_weights = []

    # Adds weights based on length
    for x in select_list:
        total += 1 / len(x)
        cum_weights.append(total)

    # Chooses element and returns
    x = random() * total
    return select_list[bisect_left(cum_weights, x)]


def get_adjacent_positions(x,y):
    return [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]

def generate_configuration(modules):
    """
    From a list of modules a random FESTO factory configuration is generated
    :param modules: A list of FESTO modules that do not have any connections yet
    :return: A factory configuration in the form of a dictionary of sets
    """
    configuration = {}
    for m in modules:
        configuration[m.module_id] = []

    module_ids = list(configuration.keys())
    copy_module_ids = module_ids.copy()

    # Placing the first module at center point
    placed_modules = {}
    x = choice(copy_module_ids)
    copy_module_ids.remove(x)
    placed_modules[(0, 0)] = x

    # Each module is placed adjacent to an already placed module
    for i in copy_module_ids:
        selectable = []

        for pos in list(placed_modules.keys()):
            x = pos[0]
            y = pos[1]
            selectable = selectable + get_adjacent_positions(x,y)

        # Randomly chooses one of the selectable positions and places down the module
        shuffle(selectable)
        for pos in selectable:
            if pos not in placed_modules.keys():
                placed_modules[pos] = i
                break

    # For each module, connections are established to at least one of the adjacent modules
    for pos, m in placed_modules.items():
        possible_neighbours = []
        x = pos[0]
        y = pos[1]
        possible_neighbours = get_adjacent_positions(x,y)

        # Does not pick positions where no neighbour exists
        selectable_neighbours = []
        for x in possible_neighbours:
            if x in placed_modules.keys():
                selectable_neighbours.append(placed_modules[x])

        # Creates a list of all combinations of selectable neighbours
        selectable_neighbours_combo = []
        for i in range(1, len(selectable_neighbours) + 1):
            selectable_neighbours_combo = selectable_neighbours_combo + (list(combinations(selectable_neighbours, i)))

        configuration[m]  = set(weighted_random_select(selectable_neighbours_combo))

    # From here we handle the case, where the configuration is not a single product line, but connected as islands
    id_list = list(configuration.keys())
    island_list = []

    # Creates an island list, grouping together module ids into individual islands
    while id_list:
        island = get_island(choice(id_list), configuration)
        island_list.append(island)
        id_list = [x for x in id_list if x not in island]

    # Adds connections until we have just 1 island across the configuration
    used_combinations = []

    while len(island_list) != 1:
        # Randomly chooses a pair of islands to try and connect
        pair = ()
        while not pair or pair in used_combinations:
            pair = choice(list(combinations(island_list, 2)))

        used_combinations.append(pair)

        neighbours = []
        for x in pair[0]:
            possible_neighbours = []

            # Get position of module id from the earlier placed_modules dictionary
            for pos, module_id in placed_modules.items():
                if module_id == x:
                    pos_x = pos[0]
                    pos_y = pos[1]
                    pos_list = get_adjacent_positions(pos_x,pos_y)
                    for p in pos_list:
                        if p in placed_modules.keys():
                            possible_neighbours.append(placed_modules[p])

                    # Saves all possible neighbours from x that are part of the second island
                    for y in pair[1]:
                        if y in possible_neighbours:
                            neighbours.append((x, y))

        # Randomly chooses a connection between the 2 islands.
        # Then updates the island list to include the new larger island.
        if neighbours:
            chosen_connections = [weighted_random_select(neighbours)]

            # Inserts selected connections in the configuration
            # 50% chance of flipping connection direction
            for connection in chosen_connections:
                x = random()
                if x <= 0.5:
                    connection = connection[::-1]

                configuration[connection[0]].add(connection[1])

            island_list.remove(pair[0])
            island_list.remove(pair[1])
            island_list.append(pair[0] + pair[1])

    # Adds a single exit point to the configuration
    configuration[choice(module_ids)].add(0)  # TODO: Make it possible to add more exit points

    # Sets connections in modules based on configuration
    for m in modules:
        m.set_connections(configuration)

    return Configuration(modules).is_valid(), configuration

recipes = [[[1, 2], [3, 4]],
           [[1, 2], [3, 4]]]

m1 = Module(
    module_id=1,
    work_type=1,
    processing_time=5,
    transport_time=5,
    cost_rate=5,
)

m2 = Module(
    module_id=2,
    work_type=2,
    processing_time=5,
    transport_time=10,
    cost_rate=5,
)

m3 = Module(
    module_id=3,
    work_type=2,
    processing_time=5,
    transport_time=10,
    cost_rate=5,
)

m4 = Module(
    module_id=4,
    work_type=3,
    processing_time=5,
    transport_time=5,
    cost_rate=5,
)

m5 = Module(
    module_id=5,
    work_type=3,
    processing_time=5,
    transport_time=5,
    cost_rate=5,
)

m6 = Module(
    module_id=6,
    work_type=4,
    processing_time=5,
    transport_time=5,
    cost_rate=5,
)

m7 = Module(
    module_id=7,
    work_type=4,
    processing_time=5,
    transport_time=5,
    cost_rate=5,
)

mlist = [m1, m2, m3, m4, m5, m6, m7]

config1 = {1: [2],
           2: [3],
           3: [4],
           4: [5],
           5: [6],
           6: [7],
           7: [0]}

config2 = {1: [2, 3],
           2: [4],
           3: [4],
           4: [5],
           5: [6],
           6: [7],
           7: [0]}

config3 = {1: [2],
           2: [3],
           3: [4, 5],
           4: [5],
           5: [6],
           6: [7],
           7: [0]}

config4 = {1: [2],
           2: [3],
           3: [4],
           4: [5],
           5: [6, 7],
           6: [7],
           7: [0]}

config5 = {1: [2],
           2: [3],
           3: [4],
           4: [6],
           5: [6],
           6: [7],
           7: [0]}

start_configs = [config1, config2, config3, config4, config5]

start_population = []

generate_query(len(recipes), 'temp.q')

"""
print('Making start population')
for config in start_configs:
    print('Verifying: ' + str(config))
    for m in mlist:
        m.set_connections(config)
    generate_xml(template_file='../../Modeler/iter1.xml', modules=mlist, recipes=recipes, new_file_name='temp.xml')
    result, trace = run_verifyta('temp.xml', 'temp.q', '-t 3', verifyta='../Experiments/verifyta')
    fitness = get_best_cost(result, 300)
    start_population.append((config, fitness))

def get_fitness(configuration):
    for m in mlist:
        m.set_connections(configuration)
    generate_xml(template_file='../../Modeler/iter1.xml', modules=mlist, recipes=recipes, new_file_name='temp.xml')
    result, trace = run_verifyta('temp.xml', 'temp.q', '-t 3', verifyta='../Experiments/verifyta')
    fitness = get_best_cost(result, 300)
    return fitness

print('Starting GA')
#pop = genetic_algorithm(start_population, 1000, 20, get_fitness)

best_config = {1: [2, 3],   # work 1
               2: [4],   # work 2
               3: [5],   # work 2
               4: [6],   # work 3
               5: [7],   # work 3
               6: [0],   # work 4
               7: [0]}      # work 4
for m in mlist:
    m.set_connections(best_config)

x = get_fitness(best_config)
"""

print(generate_configuration(mlist))
