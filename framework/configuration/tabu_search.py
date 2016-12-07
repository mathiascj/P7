from module import SquareModule
from UPPAAL.uppaalAPI import get_best_time
import re

VERIFYTA = '../UPPAAL/verifyta'
XML_TEMPLATE = "../../Modeler/iter3.4.1.xml"


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
        return neighbours_swap(frontier, recipes)

    def evaluate_config(config):
        """ Evaluates a configuration
        :param config: A string representing a configuration
        :return: An integer representing the evaluation of the config.
        """
        SquareModule.make_configuration(config)     # SIDE EFFECT: Makes loads of changes to modules
        modules = SquareModule.modules_in_config(config)
        evaluation, worked_on, transported_through = get_best_time(recipes, modules, XML_TEMPLATE, VERIFYTA)
        return evaluation

    # Memory used for remembering evalutations, used so we dont have to evaluate the same configuration twice.
    dynamic_memory = {}

    # Tabu Search specific memories
    long_term_memory = []
    intermediate_memory = []
    short_term_memory = []

    # Creating the initial configuration and evalutates it
    init_config = init_func(recipes, modules, None)
    init_modules = SquareModule.modules_in_config(init_config)
    init_time,worked_on, transported_through = get_best_time(recipes, init_modules, XML_TEMPLATE, VERIFYTA)
    dynamic_memory[init_config] = init_time

    overall_best = (init_config, init_time)
    frontier = (init_config, init_time)

    # Here begins the actual search
    for _ in range(iters):  # TODO: Maybe have stopping criteria instead of iterations, or allow for both.
        # TODO: Actually start doing Tabu like search stuff here, i.e. use memories, backtrace and shit.
        SquareModule.make_configuration(frontier[0])
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


def neighbours_swap(frontier, recipes):
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
        config_str = SquareModule.configuration_str(old)
        l = config_str.split(sep=':')
        for i, m_str in enumerate(l):
            m_str_id = re.search('(.*)(?=\{)', m_str).group(0)
            if str(old.m_id) == m_str_id:
                new_half = new.module_str().split('{')[0]
                old_half = old.module_str().split('{')[1]
                l[i] = new_half + '{' + old_half # Everything  old could do, new now can do
            else:
                split = m_str.find('[')
                s = m_str[:split]
                s += m_str[split:].replace(old.m_id, new.m_id)  # We replace all instances of the old mid with the new
                l[i] = s

        l.sort()    # TODO: I think text based sorting works, I am not sure.
        new_config_str = ':'.join(l)
        return new_config_str

    config_str = frontier[0]
    config_modules = SquareModule.modules_in_config(config_str)
    free_modules = SquareModule.modules_not_in_config(config_str)

    neighbours = []
    for old in config_modules:
        swappable = [new for new in free_modules if old.active_w_type <= new.w_type]
        for new in swappable:
            neighbours.append(swap(old, new))
    return neighbours

