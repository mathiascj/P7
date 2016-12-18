def neighbours_swap(frontier, csh):
    """ Finds all neighbours where we can swap modules out, but still retain the same active works
    :param frontier: The config that the tabu search is currently finding neighbours for
    :param recipes: A list of Recipe objects
    :return:
    """

    def swap(frontier, csh, m0, m1):
        """
        :param frontier:
        :param csh:
        :param m0:
        :param m1:
        :return:
        """
        csh.make_configuration(frontier)
        csh.swap_modules(m0, m1)
        return csh.configuration_str()

    def internal_swap_neighbours(frontier, csh, config_modules):
        neighbours = []
        for m0 in config_modules:
            csh.make_configuration(frontier)
            if m0.active_w_type is not set():
                swappable = [m1 for m1 in config_modules if m0.active_w_type == m1.active_w_type
                                                         and m0 != m1
                                                         and m1.active_w_type is not set()]
                for m1 in swappable:
                    neighbours.append(swap(frontier, csh, m1, m0))
        return neighbours

    def external_swap_neighbours(frontier, csh, config_modules, free_modules):
        neighbours = []
        for old in config_modules:
            csh.make_configuration(frontier)
            if old.active_w_type is not set():
                swappable = [new for new in free_modules if old.active_w_type <= new.w_type
                                                         and old != new
                                                         and new.active_w_type is not set()]
                for new in swappable:
                    neighbours.append(swap(frontier, csh, old, new))
        return neighbours

    config_str = frontier
    config_modules = csh.modules_in_config(config_str)
    free_modules = csh.modules_not_in_config(config_str)

    external_neighbours = external_swap_neighbours(frontier, csh, config_modules, free_modules)
    internal_neighbours = internal_swap_neighbours(frontier, csh, config_modules)

    return list(set(external_neighbours + internal_neighbours))