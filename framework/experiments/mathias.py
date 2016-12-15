from module import SquareModule
from recipe import Recipe
from configuration.tabu_search import *
from UPPAAL.uppaalAPI import get_best_time
from networkx import nx
from random import shuffle
from configuration.initial_config import initial_configuration_generator
from configuration.config_string_handler import ConfigStringHandler
from configuration.path_placers import push_underneath


VERIFYTA = '../UPPAAL/verifyta'
XML_TEMPLATE = "../../Modeler/iter3.4.2.xml"

t = [[0, 0, 0, 0],
     [0, 0, 0, 0],
     [0, 0, 0, 0],
     [0, 0, 0, 0]]

transporter = SquareModule('transporter', {}, t, 3)

m0 = SquareModule('hammer-maskine', {'hammer': 10, 'mere hammer': 10}, t, 3)

m1 = SquareModule('skrue-maskine', {'skrue': 10}, t, 3)

m2 = SquareModule('pakke-maskine', {'pakke': 10}, t, 3)

m6 = SquareModule('Smadremanden', {'smadre': 10}, t, 3)


m3 = SquareModule('super-skruer', {'skrue': 4}, t, 3)
m4 = SquareModule('super-pakker', {'pakke': 2}, t, 3)

m9 = SquareModule('skrue-pakke', {'skrue': 4, 'pakke': 2}, t, 3)

m5 = SquareModule('smadre-manden', {'smadre': 50}, t, 3)

m7 = SquareModule('spise-maskine', {'spise': 5}, t, 5)
m8 = SquareModule('sove-maskine',  {'sove': 5}, t, 5)

r0 = Recipe('chokolade', {'hammer': set(), 'mere hammer': {'hammer'}, 'skrue': {'mere hammer'}, 'pakke': {'skrue'}}, 'hammer-maskine', 0, 2)
r1 = Recipe('FuckMigUp', {'smadre': set()}, 'balh', 0, 2)

r2 = Recipe('chokolade', {'hammer': set(), 'skrue': {'hammer'}, 'pakke': {'skrue'}}, 'hammer-maskine', 0, 2)
r3 = Recipe('menneske', {'hammer': set(), 'spise': {'hammer'}, 'sove': {'spise'}, 'pakke': {'sove'}}, 'hammer-maskine', 0, 2)

recipes = [r2, r3]
modules = [m0, m1, m2, m8, m3, m4, m9]

csh = ConfigStringHandler(recipes, modules, transporter)
csh.main_line = [m0, m1, m2, m8, m3]


m0.right = m1
m1.right = m2
m2.right = m8
m8.right = m3

m0.active_w_type = {'hammer', 'mere hammer'}
m1.active_w_type = {'skrue'}
m2.active_w_type = {'pakke'}
m8.active_w_type = {'sove'}
m3.active_w_type = {'skrue'}

csh.current_modules = modules[:-2]
csh.free_modules = modules[-2:]

frontier = csh.configuration_str()

neighbours = neighbours_swap(frontier, csh)

for n in neighbours:
    print(n)


