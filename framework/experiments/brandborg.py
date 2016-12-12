from module import SquareModule
from recipe import Recipe
from configuration.tabu_search import tabu_search, anti_serialize, find_lines, neighbours_anti_serialized
from UPPAAL.uppaalAPI import get_best_time
from networkx import nx
from random import shuffle
from configuration.initial_config import initial_configuration_generator
from configuration.config_string_handler import ConfigStringHandler

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

m0.active_w_type = {'hammer', 'mere hammer'}
m1.active_w_type = {'skrue'}
m2.active_w_type = {'pakke'}

m3 = SquareModule('super-skruer', {'skrue': 4}, t, 3)
m4 = SquareModule('super-pakker', {'pakke': 2}, t, 3)

m5 = SquareModule('smadre-manden', {'smadre': 50}, t, 3)

m7 = SquareModule('spise-maskine', {'spise': 5}, t, 5)
m8 = SquareModule('sove-maskine',  {'sove': 5}, t, 5)

r0 = Recipe('chokolade', {'hammer': set(), 'mere hammer': {'hammer'}, 'skrue': {'mere hammer'}, 'pakke': {'skrue'}}, 'hammer-maskine', 0, 2)
r1 = Recipe('FuckMigUp', {'smadre': set()}, 'balh', 0, 2)

r2 = Recipe('chokolade', {'hammer': set(), 'skrue': {'hammer'}, 'pakke': {'skrue'}}, 'hammer-maskine', 0, 2)
r3 = Recipe('menneske', {'spise': set(), 'sove': {'spise'}, 'pakke': {'sove'}}, 'hammer-maskine', 0, 2)

recipes = [r0, r2]
modules = [m0,m1, m2, m3, m4, m7,m8]

csh = ConfigStringHandler(recipes, modules, transporter)

#gen = initial_configuration_generator(recipes, modules, csh)

m0.right = m7
m7.right = m8
m8.right = m3
m3.right = m4
m4.right = m1
m1.right = m2

csh.current_modules = modules
print(csh.configuration_str())

# s = anti_serialize(None, [m7, m3, m4, m8], m2, csh)
# print(s)

# csh.make_configuration(s)

time, worked, transported = get_best_time(recipes, modules, XML_TEMPLATE,VERIFYTA)
main_line, up_line, down_line =find_lines(csh)

neighbours_anti_serialized(worked, main_line, csh)




#for x in gen:
#     print(x)
#     csh.make_configuration(x)
#     time, _, _ = get_best_time(csh.recipes, csh.current_modules, XML_TEMPLATE, VERIFYTA)
#     print(time)
# csh.reset_modules()
#
# csh.current_modules = modules[:5]
# m0.up = m1
# m0.right = m2
# m1.right = m3
# m2.up = m4
#
# print(csh.grid_conflicts())

