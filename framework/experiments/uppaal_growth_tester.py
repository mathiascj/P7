from UPPAAL.verifytaAPI import run_verifyta, pprint
from time import time
from UPPAAL.xml_generator import generate_xml
from module import SquareModule
from recipe import Recipe
import re


template = '../../Modeler/iter3.4.2.xml'

temp_XML = 'temp.xml'
temp_Q = 'temp.q'

V = '/home/beta/uppaal64-4.1.19/bin-Linux/verifyta'


t = [[100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100]]

m0 = SquareModule('0', {0: 60, 9: 0},  t, 3)

m1 = SquareModule('1', {1: 106},  t, 3)

m2 = SquareModule('2', {2: 582},  t, 3, allow_passthrough=True)

m3 = SquareModule('3', {3: 20}, t, 3)

m4 = SquareModule('4', {4: 68},  t, 3, allow_passthrough=True)

m5 = SquareModule('5', {5: 68},  t, 3, allow_passthrough=True)

m0.up = m1
m1.up = m2
m2.up = m3
m3.up = m4
m4.up = m5

modules = [m0, m1, m2, m3, m4, m5]

times = []
ress = []
traces = []

states = []

recipes = []
func_deps = {0: set(), 1: {0}, 2: {1}, 3: {2}, 4:  {3}, 5: {4}}

for i in range(0, 100):
    recipes.append(Recipe(func_deps, 0, 0))

for i in range(10, 11):
    try:
        generate_xml(template, modules, recipes[:i], xml_name=temp_XML, q_name=temp_Q)
        start = time()
        res, trace = run_verifyta(temp_XML, temp_Q, '-t 2', '-o 3', '-y', '-u', verifyta=V)
        end = time()
        times.append(end - start)
        ress.append(res)
        traces.append(trace)
        nstates = (int(re.search('States explored : (\d+)', res.decode()).group(1)))
        states.append((nstates, i))
        print(i)
    except:
        pass







