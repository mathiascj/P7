from framework.module import SquareModule
from framework.recipe import Recipe
from copy import deepcopy, copy
from Generation.xml_generator import generate_xml
from UPPAAL.verifytaAPI import run_verifyta, pprint
import networkx as nx
import random
import signal
import time
from Configuration.search import initial_configuration

t0 = [[100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100]]

m0 = SquareModule(0, {0, 9}, {0: 60, 9: 0},  t0, 3)

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

m5 = SquareModule(5, {5}, {5: 68},  t5, 3, allow_passthrough=True)

t6 = [[100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100]]

m6 = SquareModule(6, {6}, {6: 68},  t6, 3, allow_passthrough=True)


t7 = [[100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100]]

m7 = SquareModule(7, {7}, {7: 68},  t7, 3, allow_passthrough=True)


modules = [m0, m1, m2, m3, m4, m5, m6, m7]

# Transporter
t = [[100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100]]


func_deps1 = {0: set(), 9: {0}, 1: {9}, 4: {1}, 6: {4}, 7: {6}}
func_deps2 = {2: set(), 3: {2}, 6: {3}, 7: {6}}
func_deps3 = {0: set(), 2: {0}, 5: {2}, 6: {5}, 7: {6}}

r0 = Recipe(func_deps1, 0, 3)
r1 = Recipe(func_deps2, 2, 3)
r2 = Recipe(func_deps3, 0, 3)


x = initial_configuration([r0, r1], modules)
map = generate_xml("../../Modeler/iter3.4.1.xml", x, [r0, r1])
res, trace = run_verifyta("../../Code/Configuration/test.xml",
             "../../Code/Configuration/test.q", "-t 2 -o 3 -u",
             verifyta='/home/alexander/uppaal64-4.1.19/bin-Linux/verifyta')
