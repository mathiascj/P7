import re
from random import choice

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


def connect_module_list(list, direction='right'):
    for i, m in enumerate(list):
        if i + 1 < len(list):
            # Dynamically sets direction
            setattr(m, direction, list[i + 1])

def push_from_under(start, path, end, remaining, csh):
    """
    Pushes a new line up for remaining, having all conflicting lines move up
    :param start: Point at remaining from which we start
    :param path: Sequence of modules we with to branch out
    :param end: Point at remaining where we want to end
    :param remaining: Main line we're branching away from
    :param csh: config_string_handler
    :return:
    """


    def lines_above(line, grid, inverted_grid): #TODO gør så den kun kigger på konflikter af paralleliserings linjer
        """
        For a given line, gets all lines above which it conflicts with
        :param line: Line which we wish to look above from
        :return: list of lines that conflict
        """

        # Finds all modules which will collide when moving line upwards
        line_positions = [grid[x] for x in line]
        collision_positions = [(x, y + 1) for x, y in line_positions if (x, y + 1) in inverted_grid]
        collision_modules = [inverted_grid[x] for x in collision_positions]

        # Find all lines containing the conflicting modules.
        lines = []
        for mod in collision_modules:
            if mod not in  [y for x in lines for y in x]:  # Flattens multidim list
                lines.append(mod.get_line())

        return lines

    def move_line(line, grid, inverted_grid, csh):

        # Make sure all lines above are moved
        for l in lines_above(line, grid, inverted_grid):
            move_line(l, grid, inverted_grid)


        # Moves the given line up by 1 space
        line_start = line[0]
        line_end = line[-1]

        if line_start.in_down:
            connector = csh.take_transport_module()
            line_start.in_down.up = connector
            connector.up = line_start

        if line_end.down:
            connector = csh.take_transport_module()
            old_down = line_end.down
            line_end.down = connector
            connector.down = old_down

    grid = csh.make_grid()  # Get positions from modules, except for those in path
    inverted_grid = {v: k for k, v in grid.items()}  # Get modules from position

    # Moves all lines above it
    for l in lines_above(remaining, grid, inverted_grid):
        move_line(l, grid, inverted_grid)

    # With the new room made for it, path is inserted
    connect_module_list(path, 'right')
    start.up = path[0]
    path[-1].down = end


def place_path(start, path, end, remaining, csh):
    """
    Searches above and below already sat lines to find room.
    When room found it places down path.
    :param start: Point at which path should start on main line
    :param path:  Path we wish to branch out
    :param end: Point at which path should end on main line
    :param remaining: Sequence of modules left on main line after branch out
    :param csh: config_string_handler object
    :return:
    """

    def get_push_length(remaining, grid, inverted_grid, direction):
        """
        Finds how long we should push our path in a given direction to place it.
        :param remaining: Sequence of modules left on main line after branch out
        :param grid: Grid describing for each module where it is placed
        :param inverted_grid: Grid describing for each position, what module is placed there
        :param direction: If True we search upwards, if False we search downwards
        :return:
        """

        # Positions of all modules in remaining
        pos_on_line = [grid[x] for x in remaining]

        # Picks lambda function to search up or downwards based on direction
        if direction:
            f = lambda x: x + 1
        else:
            f = lambda x: x - 1

        # Counts up a counter until we can see no more placed modules by moving in our direction.
        counter = 0
        while True:
            # Get all positions above the currently selected positions
            pos_on_line = [(x, f(y)) for x, y in pos_on_line if (x, f(y)) in inverted_grid]
            if pos_on_line:
                counter += 1
            else:
                break

        return counter

    def vertical_sequence(initial, counter, grid, inverted_grid, direction, csh):
        """
        Calculates a vertical sequence for counter steps
        :param initial: Module from which sequence starts
        :param counter: Number of steps upwards
        :param grid: dict for module to position
        :param inverted_grid: dict for position to module
        :param direction: If true sequence goes upwards. If false sequence goes downwards.
        :param csh: config_string_handler
        :return:
        """

        # Picks lambda function to search up or downwards based on direction
        if direction:
            f = lambda x: x + 1
        else:
            f = lambda x: x - 1

        current = initial
        sequence = [initial]
        while 0 < counter:
            x, y = grid[current]
            next_pos = (x, f(y))
            # If there's already a module here we can move through it
            if next_pos in inverted_grid:
                next_mod = inverted_grid[next_pos]
            # if there is not a module, we append with a transport
            else:
                next_mod = csh.take_transport_module()

            sequence.append(next_mod)
            current = next_mod
            counter -= 1

        return sequence

    grid = csh.make_grid()  # Get positions from modules, except for those in path

    inverted_grid = {v: k for k, v in grid.items()}  # Get modules from position

    # Find length we have to move path upwards
    up_length = get_push_length(remaining, grid, inverted_grid, True)

    # Find length we have to move path downwards
    down_length = get_push_length(remaining, grid, inverted_grid, False)

    # Set length and direction in which to push the path
    if up_length <= down_length:
        length = up_length
        direction = True
        branch_out_direction = 'up'
        branch_in_direction = 'down'
    else:
        length = down_length
        direction = False
        branch_out_direction = 'down'
        branch_in_direction = 'up'

    # Connect path together
    connect_module_list(path, 'right')

    if start:
        # Connect from a start point to the path
        out_branch = vertical_sequence(start, length, grid, inverted_grid, direction, csh)
        out_branch.append(path[0])
        connect_module_list(out_branch, branch_out_direction)

    if end:
        # Connect from a end point to the path
        in_branch = vertical_sequence(end, length, grid, inverted_grid, direction, csh)
        in_branch.append(path[-1])
        in_branch.reverse()
        connect_module_list(in_branch, branch_in_direction)


def anti_serialize(start, path, end, csh):
    """
    Creates an anti-serialized configuration
    :param start: start module on main line
    :param path: sequence of modules to anti serialize
    :param end: end module on main line
    :param csh: configuration_string_handler_object
    :return: A string representing the new configuration
    """

    def remaining_modules(modules, path):
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
    place_path(start, path, end, remaining, csh)
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
    line, _, _ = csh.find_lines()


    # Get dict where each recipe is a key to the modules worked on by it
    iworked = invert_dict(worked)

    recipes = {}
    # Get recipes worked on the line
    for name, mods in iworked.items():
        for m in mods:
            if csh.module_dictionary[m] in line:
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

    for mod in line:
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