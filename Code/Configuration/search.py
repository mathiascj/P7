from framework.module import SquareModule
from framework.recipe import Recipe
from copy import deepcopy, copy
from Generation.xml_generator import generate_xml
from UPPAAL.verifytaAPI import run_verifyta, pprint
import networkx as nx
import random
from UPPAAL.uppaalAPI import get_best_time
import signal
import time

VERIFYTA = '/home/beta/uppaal64-4.1.19/bin-Linux/verifyta'
XML_TEMPLATE = "../../Modeler/iter3.4.1.xml"

signal.signal(signal.SIGINT, signal.default_int_handler)

def create_transporters(amount, time, queue_size):
    transporters = []
    for i in range(amount):
        t = SquareModule('trans_' + str(i), [], {}, time, queue_size, allow_passthrough= True)
        transporters.append(t)
    return transporters


def get_factorial_list(nodes):
    n = []
    for i in range(1, len(nodes) + 1):
        n.append({x for j, x in enumerate(nodes) if j < i})

    return n

def initial_configuration(recipes, modules, transporters=None):
    G = Recipe.get_flow_graph(recipes)
    G.reverse()
    Recipe.plot(G)
    G_copy = nx.topological_sort(G)

    conf = []
    while G_copy:
        size = 0
        current = None
        for i, n in enumerate(get_factorial_list(G_copy)):
            l = [m for m in modules if m.w_type >= n]
            if l:
                current = l
                size = i + 1
                continue
            else:
                break

        smallest_len = len(G)
        candidate = None
        for m in current:
            if len(m.w_type) <= smallest_len:
                smallest_len = len(m.w_type)
                candidate = m

        candidate.active_w_type = set(G_copy[:size])
        conf.append(candidate)
        G_copy = G_copy[size:]

    for i, m in enumerate(conf):
        if i < len(conf) - 1:
            m.right = conf[i + 1]

    return conf

def tabu_search(recipes, modules, transporters, init_func):
    init_config = init_func(recipes, modules, transporters)
    free_modules = [m for m in modules if m not in init_config]
    
    #init_time = get_best_time(recipes, init_config, XML_TEMPLATE, VERIFYTA)

    #current_best = (SquareModule.configuration_str(init_config[0]), init_time)

    long_term_memory = []
    intermediate_memory = []
    short_term_memory = []

    #return current_best


def get_neighbours(config, recipes, free_modules, free_transporters):
    return get_swap_neighbours(config, recipes, free_modules, free_transporters)

def get_swap_neighbours(config, recipes, free_modules, free_transporters):
    L = []
    for m in config:
        for fm in free_modules:
            if m.active_w_type <= fm.w_type:
                L.append((m, fm))

    m, fm = random.choice(L)
    m.swap(fm)

