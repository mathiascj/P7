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

m0 = SquareModule('m0', {'w0': 60},  t, 3)

m1 = SquareModule('m1', {'w1': 106},  t, 3)

m2 = SquareModule('m2', {'w2': 582},  t, 3)

m3 = SquareModule('m3', {'w3': 20}, t, 3)

m4 = SquareModule('m4', {'w4': 68},  t, 3)

m5 = SquareModule('m5', {'w5': 68},  t, 3)

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

func_deps = {'w0': set(), 'w1': {'w0'}, 'w2': {'w1'}, 'w3': {'w2'}, 'w4':  {'w3'}, 'w5': {'w4'}}
recipes = Recipe('r0', func_deps, 0, 0, 1)

for i in range(101, 152, 10):
        generate_xml(template, modules, [Recipe('kage', func_deps, 'm0', 0, i)], xml_name=temp_XML, q_name=temp_Q)
        start = time()
        res, trace = run_verifyta(temp_XML, temp_Q, '-t 2', '-o 3', '-y', '-u', verifyta=V)
        end = time()
        time_res = end - start

        times.append(time_res)
        ress.append(res)
        traces.append(trace)
        nstates = (int(re.search('States explored : (\d+)', res.decode()).group(1)))
        states.append((nstates, i))
        print(str(i) + "\t\tstates: " + str(nstates) + "\t\ttime: " + str(time_res))








