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

m0.active_w_type = {'hammer', 'mere hammer'}
m1.active_w_type = {'skrue'}
m2.active_w_type = {'pakke'}

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
csh.main_line = [m0, m1, m2, m8]

#gen = initial_configuration_generator(recipes, modules, csh)

m0.right = m1
m1.right = m2
m2.right = m8

csh.current_modules = modules[:-3]
csh.free_modules = modules[-3:]

frontier = csh.configuration_str()

csh.make_configuration(frontier)

res = parallel_args(m0.traverse_right(), csh.free_modules, csh)


def update_config(frontier, start, path, end, csh, direction):
    csh.make_configuration(frontier)
    t0 = csh.take_transport_module()
    t1 = csh.take_transport_module()

    for i, m in enumerate(start.traverse_right(end)[1:]):
        path[i].active_w_type = m.active_w_type.copy()
    csh.current_modules += [t0, t1]
    expanded_path = [t0] + path + [t1]

    push_underneath(start, expanded_path, end, csh, direction)

    result = csh.configuration_str()

    csh.free_transport_module(t0)
    csh.free_transport_module(t1)

    return result

config_strings = []
for r in res:
    config_strings.append(update_config(frontier, *r, csh, 'down'))

csh.make_configuration(config_strings[0])
csh.find_lines()

for s in config_strings:
    print(s)

#res = helper(capable_modules(m1.active_w_type, csh.free_modules), m2.traverse_right(), csh.free_modules)
#t = get_best_time(csh.recipes, csh.current_modules, XML_TEMPLATE, VERIFYTA)


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

