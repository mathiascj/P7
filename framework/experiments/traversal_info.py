from UPPAAL.uppaalAPI import get_best_time
from configuration.config_string_handler import ConfigStringHandler
from module import SquareModule
from recipe import Recipe

VERIFYTA = '../UPPAAL/verifyta'
XML_TEMPLATE = "../../Modeler/iter3.4.2.xml"

t = [[0, 0, 0, 0],
     [0, 0, 0, 0],
     [0, 0, 0, 0],
     [0, 0, 0, 0]]

m0 = SquareModule('hammer-maskine', {'hammer': 10, 'mere hammer': 10}, t, 3)

m1 = SquareModule('skrue-maskine', {'skrue': 10}, t, 3)

m2 = SquareModule('pakke-maskine', {'pakke': 10}, t, 3)

m0.active_w_type = {'hammer', 'mere hammer'}
m1.active_w_type = {'skrue'}
m2.active_w_type = {'pakke'}

m3 = SquareModule('super-skruer', {'skrue': 4}, t, 3)
m4 = SquareModule('super-pakker', {'pakke': 2}, t, 3)


m0.up = m3
m3.up = m1
m1.up = m2

r0 = Recipe('chokolade', {'hammer': set(), 'mere hammer': {'hammer'}, 'skrue': {'mere hammer'}, 'pakke': {'skrue'}}, 'hammer-maskine', 0, 4)
r1 = Recipe('kage', {'hammer': set(), 'mere hammer': {'hammer'}, 'skrue': {'mere hammer'}, 'pakke': {'skrue'}}, 'hammer-maskine', 0, 4)

s = r0.recipe_str() + '|' + m0.modules_str()

c = ConfigStringHandler([r0, r1], [m0, m1, m2, m3, m4], s)

time, worked, traveled = get_best_time([r0], [m0, m1, m2, m3], XML_TEMPLATE, VERIFYTA)

def invert_dict(d):
    res = {}
    for k in d:
        for v in d[k]:
            res.setdefault(v, set()).add(k)
    return res

def something(worked, traveled):
    iworked = invert_dict(worked)
    itraveled = invert_dict(traveled)
    return {key: itraveled[key] - iworked[key] for key in iworked}

