from configuration.path_placers import connect_module_list, push_around, push_underneath
from random import choice


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


def neighbours_anti_serialized(frontier, csh, worked):
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