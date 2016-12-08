import re

from UPPAAL.uppaalAPI import get_best_time
from configuration.config_string_handler import ConfigStringHandler
from configuration.initial_config import initial_configuration_generator

VERIFYTA = '../UPPAAL/verifyta'
XML_TEMPLATE = "../../Modeler/iter3.4.2.xml"


def tabu_search(recipes, modules, iters=50):
    """ Tabu Search
    :param recipes: A list of Recipe objects
    :param modules: A list of module objects
    :param init_func: A function that creates the initial configuration
    :param iters: How many iterations of Tabu search
    :return: The best configuration found by the search
    """
    def get_neighbours():
        """ Gets the neighbours of the current frontier.
        :return: A list of tuples, where the first element of the tuple is a string representing a configuration and
        the second element its evaluation.
        """
        return neighbours_swap(frontier, recipes, csh)

    def evaluate_config(config):
        """ Evaluates a configuration
        :param config: A string representing a configuration
        :return: An integer representing the evaluation of the config.
        """

        if config in dynamic_memory:
            return dynamic_memory[config]
        else:
            csh.make_configuration(config)     # SIDE EFFECT: Makes loads of changes to modules
            modules_in_config = csh.modules_in_config(config)
            evaluation, _, _ = get_best_time(recipes, modules_in_config, XML_TEMPLATE, VERIFYTA)
            dynamic_memory[config] = evaluation
            return evaluation


    csh = ConfigStringHandler(recipes, modules)
    generator = initial_configuration_generator(recipes, modules, csh)



    # Memory used for remembering evalutations, used so we dont have to evaluate the same configuration twice.
    dynamic_memory = {}

    # Tabu Search specific memories
    long_term_memory = []
    intermediate_memory = []
    short_term_memory = []

    for config in generator:
        evaluate_config(config) # Updates dynamic memory
        long_term_memory.append(config)

    # Creating the initial configuration and evalutates it
    long_term_memory.sort(key=(lambda x: dynamic_memory[x]))
    overall_best = long_term_memory[0]
    frontier = long_term_memory[0]


    # Here begins the actual search
    for _ in range(iters):  # TODO: Maybe have stopping criteria instead of iterations, or allow for both.
        # TODO: Actually start doing Tabu like search stuff here, i.e. use memories, backtrace and

        csh.make_configuration(frontier[0])
        neighbours = get_neighbours()
        neighbour_evaluations = map(evaluate_config, neighbours)
        best = min(neighbour_evaluations, key=(lambda x: x[1])) # Finds the best neighbour
        if best[1] < overall_best[1]:
            overall_best = best
        frontier = best

    return overall_best


def path_setter(start, path, end, up):
    if up:
        start.up = path[0]
        path[-1].down = end
    else:
        start.down = path[0]
        path[-1].up = end

    connect_module_list(path)


def connect_module_list(list):
    for i, m in enumerate(list):
        if i + 1 < len(list):
            m.right = list[i + 1]


def anti_serialize(start, path, end, csh):
    grid = csh.make_grid()


    if start and end:
        mods = start.traverse_right(end)
        remaining = [x for x in mods if x not in path]
        # When path is too short
        while len(remaining) > len(path):
            path.append(csh.take_transport_module())

        # When path is too long
        end = remaining[-1]
        remaining.remove(end)
        while len(remaining) < len(path) - 1:
            remaining.append(csh.take_transport_module())
        remaining.append(end)

        # Reconnect original line
        connect_module_list(remaining)

        # Reset connections in new line
        for m in path:
            m.right = None

        # Tries to set new line above
        path_setter(start, path, end, True)
        if not csh.grid_conflicts():
            return csh.configuration_str()

        # Tries to set new line below
        path_setter(start, path, end, False)
        if not csh.grid_conflicts:
            return csh.configuration_str()

    elif end:
        mods = end.traverse_in_left()
        remaining = [x for x in mods if x not in path]
        remaining.reverse()
        connect_module_list(remaining)

        for m in path:
            m.right = None
        connect_module_list(path)

        path[-1].down = end
        path[-1].right = None
        if not csh.grid_conflicts():
            return csh.configuration_str()

        path[-1].down = None
        path[-1].up = end
        if not csh.grid_conflicts():
            return csh.configuration_str()

    elif start:
        mods = start.traverse_right()
        remaining = [x for x in mods if x not in path]
        connect_module_list(remaining)

        for m in path:
            m.right = None
        connect_module_list(path)
        start.up =  path[0]

        if not csh.grid_conflicts():
            return csh.configuration_str()

        start.up = None
        start.down = path[0]
        if not csh.grid_conflicts():
            return csh.configuration_str()


    return ""



def neighbours_swap(frontier, recipes, csh):
    """ Finds all neighbours where we can swap modules out, but still retain the same active works
    :param frontier: The config that the tabu search is currently finding neighbours for
    :param recipes: A list of Recipe objects
    :return:
    """
    def swap(old, new):
        """ Does the actual swap in the configuration
        :param old: The modules you wish to swap out
        :param new: The module that you wish to swap in
        :return: A new configuration string, where we swapped old with new
        """
        config_str = csh.configuration_str()
        S = config_str.split('|')
        M = S[1].split(sep=':')
        for i, m_str in enumerate(M):
            m_str_id = re.search('(.*)(?=\{)', m_str).group(0)
            if str(old.m_id) == m_str_id:
                new_half = new.module_str().split('{')[0]
                old_half = old.module_str().split('{')[1]
                M[i] = new_half + '{' + old_half # Everything  old could do, new now can do
            else:
                split = m_str.find('[')
                s = m_str[:split]
                s += m_str[split:].replace(old.m_id, new.m_id)  # We replace all instances of the old mid with the new
                M[i] = s

        M.sort()    # TODO: I think text based sorting works, I am not sure.
        new_config_str = S[0] + '|' + ':'.join(M)
        return new_config_str

    config_str = frontier[0]
    config_modules = csh.modules_in_config(config_str)
    free_modules = csh.modules_not_in_config(config_str)

    neighbours = []
    for old in config_modules:
        swappable = [new for new in free_modules if old.active_w_type <= new.w_type]
        for new in swappable:
            neighbours.append(swap(old, new))
    return neighbours

def neighbours_anti_serialized(worked, transported, line, csh):
    #Todo: Handle different lines. Handle that we have to antiserialize even on outer lines

    def invert_dict(d):
        """
        Inverts a dictionary many to many
        :param d: dictionary
        :return: inverted dictionary
        """
        res = {}
        for k in d:
            for v in d[k]:
                res.setdefault(v, set()).add(k)

        return res


    def anti_serialize_args(recipe_name, modules, csh, end_group=False):
        """
        Given a sequence of modules, finds which the anti-serialization should start and end on
        :param recipe_name: Name of recipe object
        :param modules: module sequence we wish to anti serialize
        :param csh: config_string_handler object
        :param end_group: If true, allows for end to be None so that we may branch off at end
        :return: list of arguments to anti_serialize
        """

        # Set start
        if csh.recipe_dictionary[recipe_name].start_module == modules[0]:
            start = None
        elif modules._in_left :
            start = modules._in_left
        else:
            return None #TODO: Return something so we don't throw exceptions

        # Set end
        if end_group:
            end = None
        else:
            end = modules.right

        # Set up args
        return [start, modules, end, csh]


    # Get dict where each recipe is a key to the modules worked on by it
    iworked = invert_dict(worked)


    r0_name, r0 = iworked.items()[0]
    r1_name, r1 = iworked.items()[1]
    split_groups = []
    current_group = []

    for m in line:
        # When m is a common module between r0 and r1
        if m in r0 and m in r1 and not current_group:
                # Finds start and end modules for the path
                split_groups.append(anti_serialize_args(r0_name, current_group, csh))
                current_group = []

        # If m is only in r0 we append it to the current_group
        elif m in r0:
            current_group.append(m)

    # Gets start and end for last path found
    # Also allows for end to be set to None
    if current_group:
        split_groups.append(anti_serialize_args(r0_name, current_group, csh, True))


    # Call arguments of each split on anti_serialize.
    for splits in split_groups:
        print(anti_serialize(*splits))


