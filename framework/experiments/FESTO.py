from module import SquareModule
from recipe import Recipe
from configuration.tabu_search import tabu_search
from UPPAAL.uppaalAPI import get_best_time
VERIFYTA = '../UPPAAL/verifyta'
XML_TEMPLATE = "../../Modeler/iter3.4.2.xml"

QUEUE_LENGTH = 3


t0 = [[0, 0, 0, 0],
     [0, 0, 0, 0],
     [0, 0, 0, 0],
     [0, 117, 0, 0]]
m0 = SquareModule('Case Loader', {'load case': 60}, t0, QUEUE_LENGTH)

t1 = [[0, 0, 0, 0],
     [0, 0, 0, 0],
     [0, 0, 0, 0],
     [0, 107, 0, 0]]
m1 = SquareModule('Drill', {'drill1': 53, "drill2":106 }, t1, QUEUE_LENGTH)

t2 = [[0, 0, 0, 0],
     [0, 0, 0, 0],
     [0, 0, 0, 0],
     [0, 164, 0, 0]]
m2 = SquareModule('Robot Arm', {'fuse0': 582, "fuse1":752, "fuse2":850 }, t2, QUEUE_LENGTH)


t3 = [[0, 0, 0, 0],
     [0, 0, 0, 0],
     [0, 0, 0, 0],
     [0, 112, 0, 0]]
m3 = SquareModule('camera', {'picture': 20}, t3, QUEUE_LENGTH)


t4 = [[0, 0, 0, 0],
     [0, 0, 0, 0],
     [0, 0, 0, 0],
     [0, 112, 0, 0]]
m4 = SquareModule('Transport0', {}, t4, QUEUE_LENGTH)

t5 = [[0, 0, 0, 0],
     [0, 0, 0, 0],
     [0, 0, 0, 0],
     [0, 0, 0, 0]]
m5 = SquareModule('Package', {'pack': 68}, t5, QUEUE_LENGTH)


m0.right = m1
m1.right = m2
m2.right = m3
m3.right = m4
m4.right = m5

m2.allow_passthrough = True

r0 = Recipe('NoFuse', {'load case': set(), 'drill2': {'load case'}, 'fuse0': {'drill2'}, 'picture':{'fuse0'}, 'pack':{'picture'}}, 'Case Loader', 3, 1)
r1 = Recipe('LeftFuse', {'load case': set(), 'drill1': {'load case'}, 'fuse1': {'drill1'}, 'picture':{'fuse1'}, 'pack':{'picture'}}, 'Case Loader', 3, 1)
r2 = Recipe('BothFuse', {'load case': set(), 'drill2': {'load case'}, 'fuse2': {'drill2'}, 'picture':{'fuse2'}, 'pack':{'picture'}}, 'Case Loader', 3, 1)

recipes = [r0 , r1, r2]
modules = [m0, m1, m2, m3, m4, m5]

time, __, _, _ = get_best_time(recipes, modules, XML_TEMPLATE, VERIFYTA )
print(time)