from module import SquareModule
from recipe import Recipe
from configuration.tabu_search import *
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

m9 = SquareModule('skrue-pakke', {'skrue': 4, 'pakke': 2}, t, 3)

m5 = SquareModule('smadre-manden', {'smadre': 50}, t, 3)

m7 = SquareModule('spise-maskine', {'spise': 5}, t, 5)
m8 = SquareModule('sove-maskine',  {'sove': 5}, t, 5)

r0 = Recipe('chokolade', {'hammer': set(), 'mere hammer': {'hammer'}, 'skrue': {'mere hammer'}, 'pakke': {'skrue'}}, 'hammer-maskine', 0, 2)
r1 = Recipe('FuckMigUp', {'smadre': set()}, 'balh', 0, 2)

r2 = Recipe('chokolade', {'hammer': set(), 'skrue': {'hammer'}, 'pakke': {'skrue'}}, 'hammer-maskine', 0, 2)
r3 = Recipe('menneske', {'hammer': set(), 'spise': {'hammer'}, 'sove': {'spise'}, 'pakke': {'sove'}}, 'hammer-maskine', 0, 2)

recipes = [r2, r3]
modules = [m0, m1, m2, m3, m4, m9]

csh = ConfigStringHandler(recipes, modules, transporter)

#gen = initial_configuration_generator(recipes, modules, csh)

m0.right = m1
m1.right = m2

csh.current_modules = modules[:-3]
csh.free_modules = modules[-3:]

frontier = csh.configuration_str()


def starter(line, free_modules):
    temp = []
    for split, m in enumerate(line):
        cm = capable_modules(m.active_w_type, free_modules)
        temp.append((m, helper(cm, line[split + 1:], free_modules)))

    # Check whether or not we can attach this path to a start and end and that the path has an actual length


    result = [r for r in temp if r[0].in_left and r[1]]
    for r in result:
        r_len =  len(r[0].traverse_right())
        for path in r[1]:
            if r_len <= len(r[1]):
                r[1].remove(path)


    return result



def helper(capable, remaining, free_modules):
    result = []
    if capable:
        for c in capable:
            fm = free_modules.copy()
            fm.remove(c)
            temp = []
            if remaining:
                next_capable = capable_modules(remaining[0].active_w_type, fm)
                temp = helper(next_capable, remaining[1:], fm)
            if temp:
                for l in temp:
                    result.append([c] + l)
            result.append([c])

    return result

csh.make_configuration(frontier)
res = starter(m0.traverse_right(), csh.free_modules)
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

