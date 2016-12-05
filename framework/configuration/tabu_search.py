from module import SquareModule
from UPPAAL.uppaalAPI import get_best_time

VERIFYTA = '/home/beta/uppaal64-4.1.19/bin-Linux/verifyta'
XML_TEMPLATE = "../../Modeler/iter3.4.1.xml"


def tabu_search(recipes, modules, init_func):
    init_config = init_func(recipes, modules, None)
    free_modules = [m for m in modules if m not in init_config]
    
    init_time = get_best_time(recipes, init_config, XML_TEMPLATE, VERIFYTA)

    current_best = (SquareModule.configuration_str(init_config[0]), init_time)
    current_frontier = (SquareModule.configuration_str(init_config[0]), init_time)

    long_term_memory = []
    intermediate_memory = []
    short_term_memory = []

    for i in range(100):
        neighbours = get_neighbours(current_frontier, recipes, free_modules, transporters)
        short_term_memory += neighbours
        best = min(neighbours, key=(lambda x: x[1]))
        if best[1] < current_best[1]:
            current_best = best
        current_frontier = best

    return current_best
