from UPPAAL.verifytaAPI import run_verifyta, pprint
from time import time

XML = '../../Modeler/iter3.1.xml'
XML2 = '../../Modeler/iter3.2.xml'
Q = '../../Modeler/iter3.q'
V = '../UPPAAL/verifyta'

times = []
ress = []


start = time()
res, trace = run_verifyta(XML, Q, '-t 3', '-o 3', '-u', verifyta=V)
end = time()
print('Done \n TIME:' + str(end - start))
pprint(res)
times.append(end - start)
ress.append(res)

start = time()
res, trace = run_verifyta(XML2, Q, '-t 3', '-o 3', '-u', verifyta=V)
end = time()
print('Done \n TIME:' + str(end - start))
pprint(res)
times.append(end - start)
ress.append(res)