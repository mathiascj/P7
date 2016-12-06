from module import SquareModule
from recipe import Recipe
from UPPAAL.xml_generator import generate_xml
from UPPAAL.verifytaAPI import run_verifyta
import re
from configuration.initial_config import initial_configuration

t0 = [[100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100]]

m0 = SquareModule(0,  {"0": 60, "9": 0},  t0, 3)

t1 = [[100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100]]

m1 = SquareModule(1,  {"1": 106},  t1, 3)

t2 = [[100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100]]

m2 = SquareModule(2,  {"2": 582},  t2, 3, allow_passthrough=True)

t3 = [[100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100]]

m3 = SquareModule(3,  {"3": 20}, t3, 3)

t4 = [[100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100]]

m4 = SquareModule(4,  {"4": 68},  t4, 3, allow_passthrough=True)

t5 = [[100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100]]

m5 = SquareModule(5,  {"5": 68},  t5, 3, allow_passthrough=True)

t6 = [[100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100]]

m6 = SquareModule(6, {"6": 68},  t6, 3, allow_passthrough=True)


t7 = [[100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100]]

m7 = SquareModule(7, {"7": 68},  t7, 3, allow_passthrough=True)


modules = [m0, m1, m2, m3, m4, m5, m6, m7]

# Transporter
t = [[100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100],
      [100, 100, 100, 100]]

func_deps1 = {"0": set(), "9": {"0"}, "1": {"9"}, "4": {"1"}, "6": {"4"}, "7": {"6"}}
func_deps2 = {"2": set(), "3": {"2"}, "6": {"3"}, "7": {"6"}}
func_deps3 = {"0": set(), "2": {"0"}, "5": {"2"}, "6": {"5"}, "7": {"6"}}

r0 = Recipe("Jens", func_deps1, 0, 3, 1)
r1 = Recipe("Karl", func_deps2, 2, 3, 9)
r2 = Recipe("Bob", func_deps3, 0, 3, 3)


x = initial_configuration([r0, r1, r2], modules)
print(x)

m_map, w_map, r_map = generate_xml("../../Modeler/iter3.4.2.xml", x, [r0, r1, r2])
print(m_map)
print(w_map)
print(r_map)

res, trace = run_verifyta("test.xml",
             "test.q", '-t 2', '-o 3', '-y', '-u',
             verifyta='../UPPAAL/verifyta')


print(res)

text_file = open("Output.txt", "w")
text_file.write(trace.decode('utf-8'))
text_file.close()


is_transition = False
is_handshake = False


worked_on = {}
with open("Output.txt") as f:
    for line in f:
        if line == "Transitions:\n":
                lines = []
                counter = 0
                for line in f:
                    lines.append(line)
                    counter += 1
                    if counter == 2:
                        break
                counter = 0
                if "handshake" in lines[0]:
                    r_id = int(re.findall("\d+", lines[0])[0])
                    w_id = int(re.findall("\d+", lines[1])[0])

                    if w_id not in worked_on:
                        worked_on[w_id] = []

                    if r_id not in worked_on[w_id]:
                        worked_on[w_id].append(r_id)


print(worked_on)