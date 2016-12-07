import re

from UPPAAL.uppaalAPI import get_best_time
from configuration.config_string_handler import ConfigStringHandler

VERIFYTA = '../UPPAAL/verifyta'
XML_TEMPLATE = "../../Modeler/iter3.4.2.xml"


def tabu_search(recipes, modules, init_func, iters=50):
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
        csh.make_configuration(config)     # SIDE EFFECT: Makes loads of changes to modules
        modules_in_config = csh.modules_in_config(config)
        evaluation, _, _ = get_best_time(recipes, modules_in_config, XML_TEMPLATE, VERIFYTA)
        return evaluation


    csh = ConfigStringHandler(recipes, modules)
    # Memory used for remembering evalutations, used so we dont have to evaluate the same configuration twice.
    dynamic_memory = {}

    # Tabu Search specific memories
    long_term_memory = []
    intermediate_memory = []
    short_term_memory = []

    # Creating the initial configuration and evalutates it
    init_config = init_func(recipes, modules, None)
    init_modules = csh.modules_in_config(init_config)
    init_time, worked_on, transported_through = get_best_time(recipes, init_modules, XML_TEMPLATE, VERIFYTA)
    dynamic_memory[init_config] = init_time

    overall_best = (init_config, init_time)
    frontier = (init_config, init_time)

    # Here begins the actual search
    for _ in range(iters):  # TODO: Maybe have stopping criteria instead of iterations, or allow for both.
        # TODO: Actually start doing Tabu like search stuff here, i.e. use memories, backtrace and shit.
        csh.make_configuration(frontier[0])
        neighbours = get_neighbours()
        neighbours_to_eval = [config for config in neighbours if config not in dynamic_memory]
        for config in neighbours_to_eval:
            evaluation = evaluate_config(config)
            dynamic_memory[config] = evaluation
        neighbour_evaluations = [(config, dynamic_memory[config]) for config in neighbours]
        best = min(neighbour_evaluations, key=(lambda x: x[1])) # Finds the best neighbour
        if best[1] < overall_best[1]:
            overall_best = best
        frontier = best

    return overall_best


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

