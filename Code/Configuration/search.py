from framework.module import SquareModule
from framework.recipe import Recipe
from collections import OrderedDict
from copy import deepcopy, copy
from Generation.xml_generator import generate_xml
from UPPAAL.verifytaAPI import run_verifyta, pprint


def create_transporters(initial_id, times, queue_size, amount):

    transporters = []
    for i in range(amount):
        t = SquareModule(initial_id, [], {}, times, queue_size, allow_passthrough= True)
        transporters.append(t)
        initial_id += 1
    return transporters


def get_factorial_list(nodes):
    n = []
    for i in range(1, len(nodes) + 1):
        n.append({x for j, x in enumerate(nodes) if j < i})

    return n

def initial_configuration(recipes, modules, transporters):
    G = Recipe.get_flow_graph(recipes)
    G = Recipe.kahn_topological_sort(G, recipes[0].start_module)
    a = G.reverse()
    Recipe.plot(a)
    G_copy = deepcopy(G.nodes())

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

        G_copy = G_copy[size:]


        smallest_len = len(G)
        candidate = None
        for m in current:
            if len(m.w_type) <= smallest_len:
                smallest_len = len(m.w_type)
                candidate = m

        conf.append(candidate)

    for i, m in enumerate(conf):
        if i < len(conf) - 1:
            m.right = conf[i + 1]

    return conf


t0 = [[100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100]]
m0 = SquareModule(0, {0}, {0: 60},  t0, 3)

t1 = [[100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100]]

m1 = SquareModule(1, {1}, {1: 106},  t1, 3)

t2 = [[100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100]]

m2 = SquareModule(2, {2}, {2: 582},  t2, 3, allow_passthrough=True)

t3 = [[100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100]]

m3 = SquareModule(3, {3}, {3: 20}, t3, 3)

t4 = [[100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100]]

m4 = SquareModule(4, {4}, {4: 68},  t4, 3, allow_passthrough=True)

t5 = [[100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100]]

m5 = SquareModule(4, {5}, {5: 68},  t5, 3, allow_passthrough=True)

t6 = [[100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100]]

m6 = SquareModule(4, {6}, {6: 68},  t6, 3, allow_passthrough=True)


t7 = [[100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100]]

m7 = SquareModule(4, {7}, {7: 68},  t7, 3, allow_passthrough=True)


modules = [m0, m1, m2, m3, m4, m5, m6, m7]

# Transporter
t = [[100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100]]

transporters = create_transporters(6, t, 3, 10)

func_deps1 = {0: set(), 1:{0}, 4:{1}, 6:{4}, 7:{6}}
func_deps2 = {0: set(), 2:{0}, 3:{2}, 6:{3}, 7:{6}}
func_deps3 = {0: set(), 2:{0}, 5:{2}, 6:{5}, 7:{6}}

r0 = Recipe(func_deps1, 0, 3)
r1 = Recipe(func_deps2, 0, 3)
r2 = Recipe(func_deps3, 0, 3)



x = initial_configuration([r0,r1,r2], modules, transporters)
generate_xml("../../Modeler/iter3.4.1.xml", x, [r0, r1, r2])
res, trace = run_verifyta("../../Code/Generation/test.xml",
             "../../Code/Generation/test.q", "-t 2 -o 3 -u",
             verifyta="/home/alexander/UPPAAL/uppaal-4.0.14/bin-Linux/verifyta")

pprint(res)