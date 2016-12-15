from module import SquareModule
from recipe import Recipe
from configuration.tabu_search import tabu_search


VERIFYTA = '../UPPAAL/verifyta'
XML_TEMPLATE = "../../Modeler/iter3.4.2.xml"

t = [[0, 0, 0, 0],
     [0, 0, 0, 0],
     [0, 0, 0, 0],
     [0, 0, 0, 0]]

QUEUE_LENGTH = 1

transporter = SquareModule('transporter', {}, t, QUEUE_LENGTH)

m0 = SquareModule('hammer-maskine', {'hammer': 10, 'mere hammer': 10}, t, QUEUE_LENGTH)

m1 = SquareModule('skrue-maskine', {'skrue': 100}, t, QUEUE_LENGTH)

m2 = SquareModule('pakke-maskine', {'pakke': 10}, t, QUEUE_LENGTH)

m6 = SquareModule('Smadremanden', {'smadre': 10}, t, QUEUE_LENGTH)

m0.active_w_type = {'hammer', 'mere hammer'}
m1.active_w_type = {'skrue'}
m2.active_w_type = {'pakke'}

m3 = SquareModule('super-skruer', {'skrue': 4}, t, QUEUE_LENGTH)
m4 = SquareModule('super-pakker', {'pakke': 2}, t, QUEUE_LENGTH)

m5 = SquareModule('smadre-manden', {'smadre': 50}, t, QUEUE_LENGTH)

m7 = SquareModule('spise-maskine', {'spise': 20}, t, QUEUE_LENGTH)
m8 = SquareModule('sove-maskine',  {'sove': 5}, t, QUEUE_LENGTH)

m9 = SquareModule('skrue-pakker', {'skrue':4, 'pakke':2},t,QUEUE_LENGTH)

r0 = Recipe('chokolade', {'hammer': set(), 'mere hammer': {'hammer'}, 'skrue': {'mere hammer'}, 'pakke': {'skrue'}}, 'hammer-maskine', 0, 2)
r1 = Recipe('FuckMigUp', {'smadre': set()}, 'balh', 0, 2)

r2 = Recipe('chokolade', {'hammer': set(), 'skrue': {'hammer'}, 'pakke': {'skrue'}}, 'hammer-maskine', 0, 2)
r3 = Recipe('menneske', {'hammer': set(), 'spise': {'hammer'}, 'sove': {'spise'}, 'pakke': {'sove'}}, 'hammer-maskine', 0, 2)

recipes = [r2, r3]
modules = [m0, m1, m2, m3, m4, m7, m8, m9]

res = tabu_search(recipes, modules, transporter)


for x in res:
     print(x + " " + str(res[x]))