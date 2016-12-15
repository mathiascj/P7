import re
from random import choice
from module import SquareModule
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
    def parallel_config_string(frontier, start, path, end, csh, direction):
        csh.make_configuration(frontier)
        t0 = csh.take_transport_module()
        t1 = csh.take_transport_module()

        for i, m in enumerate(start.traverse_right(end)[1:-1]): # check at det virker med den opdaterede traverse_right og -1
            path[i].active_w_type = m.active_w_type.copy()
        csh.current_modules += [t0, t1]
        expanded_path = [t0] + path + [t1]

        push_underneath(start, expanded_path, end, csh, direction)

        result = csh.configuration_str()

        csh.free_transport_module(t0)
        csh.free_transport_module(t1)

        return result

    csh.make_configuration(frontier)
    main_line, up_lines, down_lines = csh.find_lines()

    main_args_list = parallel_args(main_line, csh.free_modules, csh)
    main_configs = []
    for args in main_args_list:
        main_configs.append(parallel_config_string(frontier, *args, csh, 'up'))
        main_configs.append(parallel_config_string(frontier, *args, csh, 'down'))

    up_configs = []
    for up in up_lines:
        args_list = parallel_args(up, csh.free_modules, csh)
        for args in args_list:
            config = parallel_config_string(frontier, *args, csh, 'up')
            up_configs.append(config)

    down_configs = []
    for down in down_lines:
        args_list = parallel_args(down, csh.free_modules, csh)
        for args in args_list:
            config = parallel_config_string(frontier, *args, csh, 'down')
            down_configs.append(config)


    return list(set(main_configs + up_configs + down_configs))


def modules_by_worktype(modules):
    """
    :param modules: list of module objects
    :return: Dict for looking up modules from work types
    """

    res = {}
    for m in modules:
        for w in m.w_type:
            res.setdefault(w, set()).add(m)
    return res


def capable_modules(worktypes, modules):
    """
    :param worktypes: list of worktypes
    :param modules: list of modules
    :return: set of modules which may perform all worktypes
    """

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
    Creates an anti-serialized configuration string
    :param start: start module on main line
    :param path: sequence of modules to anti serialize
    :param end: end module on main line
    :param csh: configuration_string_handler_object
    :return: A string representing the new configuration
    """

    def remaining_modules(modules, path):
        """
        Calculates the sequence of modules on main line segment after anti-serialization
        :param modules: Original modules on main line segment
        :param path: The sequence of modules we wish to anti-serialize
        :return: Sequence of modules describing the new main line segment
        """
        remaining = []
        for m in modules:
            # In the case that the module is not in path
            if m not in path:
                remaining.append(m)

            # If the module is in path, but is also shadowed it has to be replaced with a transport.
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

    # Set up shadow. The sequence of modules on main line which the path projects down on.
    if start and end:
        shadow = remaining

    elif start:
        shadow = start.traverse_right_by_steps(len(path) - 1)

    elif end:
        shadow = end.traverse_in_left_by_steps(len(path) - 1)

    # Places down path where possible
    push_around(start, path, end, shadow, csh)

    csh.main_line = remaining
    return csh.configuration_str()


def neighbours_swap(frontier, csh):
    """ Finds all neighbours where we can swap modules out, but still retain the same active works
    :param frontier: The config that the tabu search is currently finding neighbours for
    :param recipes: A list of Recipe objects
    :return:
    """

    def extern_swap(frontier, csh, old, new):
        """ Does the actual swap in the configuration
        :param old: The modules you wish to swap out
        :param new: The module that you wish to swap in
        :return: A new configuration string, where we swapped old with new
        """
        csh.make_configuration(frontier)
        csh.swap_modules(old, new)

        csh.main_line = [new if m == old else m for m in csh.main_line]

        return csh.configuration_str()


    def intern_swap(frontier, csh, m0, m1):
        """
        :param frontier:
        :param csh:
        :param m0:
        :param m1:
        :return:
        """
        csh.make_configuration(frontier)

        csh.swap_modules(m0, m1)

        # swaps them in the main line aswell
        temp0 = [0 if m == m0 else m for m in csh.main_line]
        temp1 = [m0 if m == m1 else m for m in temp0]
        temp2 = [m1 if m == 0 else m for m in temp1]

        csh.main_line = temp2

        return csh.configuration_str()

    def internal_swap_neighbours(frontier, csh, config_modules):
        neighbours = []
        for m0 in config_modules:
            swappable = [new for new in config_modules if m0.active_w_type <= new.w_type and m0 != new]
            for m1 in swappable:
                neighbours.append(intern_swap(frontier, csh, m1, m0))
        return neighbours

    def external_swap_neighbours(frontier, csh, config_modules, free_modules):
        neighbours = []
        for old in config_modules:
            swappable = [new for new in free_modules if old.active_w_type <= new.w_type]
            for new in swappable:
                neighbours.append(extern_swap(frontier, csh, old, new))
        return neighbours

    config_str = frontier
    config_modules = csh.modules_in_config(config_str)
    free_modules = csh.modules_not_in_config(config_str)

    external_neighbours = external_swap_neighbours(frontier, csh, config_modules, free_modules)
    internal_neighbours = internal_swap_neighbours(frontier, csh, config_modules)

    return list(set(external_neighbours))


def neighbours_anti_serialized(worked, frontier, csh):
    """
    Gets all possible anti_serializations, when trying to split out a random recipe from main line
    :param worked: Dict saying for each module, what recipes were worked on it
    :param frontier: Configuration string, which we wish to find neighbours for
    :param csh: config_string_handler object
    :return: A list of strings, each representing a neighbouring configuration
    """
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

    # Get main line
    csh.make_configuration(frontier)
    main_line, _, _ = csh.find_lines()

    iworked = invert_dict(worked) # Looks up modules from recipes

    # Find recipes still worked on main line
    recipes = {}
    for name, mods in iworked.items():
        for m in mods:
            if csh.module_dictionary[m] in main_line:
                recipes[name] = mods
                break

    # Choose random recipe to anti-serialize
    chosen_recipe_name = choice(list(recipes.keys()))
    chosen_recipe_mods = iworked[chosen_recipe_name]

    # Remove chosen recipe
    recipes.pop(chosen_recipe_name)

    # Find all modules worked on by remaining recipes
    other_recipe_mods = set().union(*recipes.values())

    # Run over main line and note areas which may be anti-serialized
    neighbours = []
    unique_mods = []
    last_common = None

    for mod in main_line:
        # When the chosen recipe and other recipes have mod in common
        if mod.m_id in chosen_recipe_mods and mod.m_id in other_recipe_mods:
            if unique_mods:
                neighbour = [last_common, unique_mods, mod, csh]
                neighbours.append(neighbour)
                unique_mods = []
            last_common = mod

        # When mod is unique to the chosen recipe
        elif mod.m_id in chosen_recipe_mods:
            unique_mods.append(mod)

    # If possible, branches out the last found path, not branching in again
    if unique_mods:
        neighbour = [last_common, unique_mods, None, csh]
        neighbours.append(neighbour)

    results = []
    for n in neighbours:
        # Only call neighbours, where we do not remove starts and ends of other branches
        path = n[1]
        if not any(x.is_start or x.is_end for x in path):
            results.append(anti_serialize(*n))

    return results