import re
from random import choice

from UPPAAL.uppaalAPI import get_best_time
from configuration.config_string_handler import ConfigStringHandler
from configuration.initial_config import initial_configuration_generator
from configuration.path_placers import connect_module_list, push_around, push_underneath

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
            csh.make_configuration(config)  # SIDE EFFECT: Makes loads of changes to modules
            modules_in_config = csh.modules_in_config(config)
            evaluation, worked, transported = get_best_time(recipes, modules_in_config, XML_TEMPLATE, VERIFYTA)
            csh.set_active_work(worked)  # Updates active works based on the worked dict

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
        evaluate_config(config)  # Updates dynamic memory
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
        best = min(neighbour_evaluations, key=(lambda x: x[1]))  # Finds the best neighbour
        if best[1] < overall_best[1]:
            overall_best = best
        frontier = best

    return overall_best


def parallelize(start, path, end, csh):
    if start and end:
        if len(path) + 2 != len(start.traverse_right(end)):
            raise RuntimeError('Path longer than start -> end')
    for m in path:
        m.total_wipe()
    if start:
        path = [csh.take_transport_module()] + path
        start.up = path[0]
    if end:
        path = path + [csh.take_transport_module()]
        path[-1].down = end

    connect_module_list(path)

    return csh.configuration_str()


def parallel_args(line, free_modules, csh):
    temp = []
    for split, m in enumerate(line):
        cm = capable_modules(m.active_w_type, free_modules)
        temp.append((m, parallel_args_helper(cm, line[split + 1:], free_modules)))

    # Check whether or not we can attach this path to a start and end and that the path has an actual length
    for r in temp:
        r_len = len(r[0].traverse_right())
        for path in r[1].copy():
            if not r_len > len(path):
                r[1].remove(path)
    result = [r for r in temp if r[0].in_left and r[1]]

    arg_list = []

    for r in result:
        for path in r[1]:
            start = r[0].in_left
            end = r[0].traverse_right_by_steps(len(path))[-1]
            arg_list.append((start, path, end))

    return arg_list



def parallel_args_helper(capable, remaining, free_modules):
    result = []
    if capable:
        for c in capable:
            fm = free_modules.copy()
            fm.remove(c)
            temp = []
            if remaining:
                next_capable = capable_modules(remaining[0].active_w_type, fm)
                temp = parallel_args_helper(next_capable, remaining[1:], fm)
            if temp:
                for l in temp:
                    result.append([c] + l)
            result.append([c])

    return result

def neighbours_parallelize(frontier, csh):
    csh.make_configuration(frontier)

    csh.find_lines()

    push_underneath()




def modules_by_worktype(modules):
    res = {}
    for m in modules:
        for w in m.w_type:
            res.setdefault(w, set()).add(m)
    return res


def capable_modules(worktypes, modules):
    d = modules_by_worktype(modules)
    res = set(modules)
    for w in worktypes:
        if w in d:
            res = res & d[w]
        else:
            return set()
    return res


def path_setter(start, path, end, up):
    if up:
        if start:
            start.up = path[0]
        if end:
            path[-1].down = end
    else:
        if start:
            start.down = path[0]
        if end:
            path[-1].up = end

    path[-1].right = None
    connect_module_list(path)


def anti_serialize(start, path, end, csh):
    """
    Creates an anti-serialized configuration
    :param start: start module on main line
    :param path: sequence of modules to anti serialize
    :param end: end module on main line
    :param csh: configuration_string_handler_object
    :return: A string representing the new configuration
    """

    def remaining_modules(modules, path): #TODO: Opgrader til også at lave traverse. Og ikke for store i kantsitationer
        """
        Calculates the sequence of modules on main line segment after anti-serialization
        :param modules: All original modules on main line segment
        :param path: The sequence of modules we wish to anti-serialze
        :return: Sequence of modules describing the new main line segment
        """
        remaining = []
        for m in modules:
            # In the case that the module is not in path
            if m not in path:
                remaining.append(m)
            # If the module is in path, but is also shadowed it has to be replaced with a transport.
            # If not another line's end would be shifted.
            elif m.shadowed:
                remaining.append(csh.take_transport_module())

        return remaining

    # Calculates the modules of the main line segment touched by the anti-serialization
    if start and end:
        mods = start.traverse_right(end)
    elif start:
        mods = start.traverse_right()
    elif end:
        mods = end.traverse_in_left()
    else:
        raise RuntimeError('Both start and end cant be empty')

    # Gets sequence of modules remaining on main line segment
    remaining = remaining_modules(mods, path)

    # Remember how to connect main line segment to main line again
    start_connector = None
    end_connector = None
    if start:
        start_connector = start.in_left
    if end:
        end_connector = end.right

    # Clear the connections of all modules horizontally
    for m in mods:
        m.horizontal_wipe()

    if start and end:
        # If remaining is longer than path, we extend path with transports
        while len(remaining) > len(path):
            path.append(csh.take_transport_module())

        # When path is too long, append transports to main line
        end = remaining[-1]
        remaining.remove(end)
        while len(remaining) < len(path) - 1:
            remaining.append(csh.take_transport_module())
        remaining.append(end)

    # Reconnect original line
    connect_module_list(remaining, 'right')
    if start_connector:
        start_connector.right = start
    if end_connector:
        end.right = end_connector

    # Places down path where possible
    push_underneath(start, path, end, csh, True)
    return csh.configuration_str()


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
                M[i] = new_half + '{' + old_half  # Everything  old could do, new now can do
            else:
                split = m_str.find('[')
                s = m_str[:split]
                s += m_str[split:].replace(old.m_id, new.m_id)  # We replace all instances of the old mid with the new
                M[i] = s

        M.sort()  # TODO: I think text based sorting works, I am not sure.
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


def neighbours_anti_serialized(worked, frontier, csh):
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

    def anti_serialize_args(recipe_name, modules, last_common, csh, end_group=False):
        """
        Given a sequence of modules, finds which the anti-serialization should start and end on
        :param recipe_name: Name of recipe object
        :param modules: module sequence we wish to anti serialize
        :param csh: config_string_handler object
        :param end_group: If true, allows for end to be None so that we may branch off at end
        :return: list of arguments to anti_serialize
        """

        # Set start
        if csh.recipe_dictionary[recipe_name].start_module == modules[0] or not modules[0].in_left:
            start = None

        else:
            start = last_common

        # Set end
        if end_group:
            end = None
        else:
            end = modules[-1].right

        # Set up args
        return [start, modules, end, csh]


    # Get main line
    csh.make_configuration(frontier)
    main_line, _, _ = csh.find_lines()


    # Get dict where each recipe is a key to the modules worked on by it
    iworked = invert_dict(worked)

    recipes = {}
    # Get recipes worked on the line
    for name, mods in iworked.items():
        for m in mods:
            if csh.module_dictionary[m] in main_line:
                recipes[name] = mods
                break

    # Get random recipe to anti-serialize
    chosen_recipe_name = choice(list(recipes.keys()))
    chosen_recipe_mods = iworked[chosen_recipe_name]

    # Remove chosen recipe and get all modules used by the other recipes
    recipes.pop(chosen_recipe_name)
    other_recipe_mods = set().union(*recipes.values())

    split_groups = []
    current_split = []
    last_common = None

    for mod in main_line:
        # Common module
        if mod.m_id in chosen_recipe_mods and mod.m_id in other_recipe_mods:
            # If we have found modules to anti serialize, we add it to the split group
            if current_split:
                split_groups.append(anti_serialize_args(chosen_recipe_name, current_split, last_common, csh))
                current_split = []
            last_common = mod

        # Uncommon module
        elif mod.m_id in chosen_recipe_mods:
            current_split.append(mod)

    # If a common module was not at the end, we try to branch out
    if current_split:
        split_groups.append(anti_serialize_args(chosen_recipe_name, current_split, csh, True))

    neighbours = []
    # Call em all!
    for splits in split_groups:
        # TODO call only if possible
        neighbours.append(anti_serialize(*splits))

    return neighbours