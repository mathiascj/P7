import networkx as nx
from networkx import layout
import matplotlib.pyplot as plt


dep_J = {'A': set(),
         'B': set(),
         'C': {'A', 'B'},
         'D': {'B'},
         'E': set(),
         'F': {'C'},
         'G': {'D', 'E'},
         'H': {'F'},
         'I': {'G'},
         'J': {'H', 'I'}}

dep_K = {'B': set(),
         'D': {'B'},
         'E': set(),
         'G': {'D', 'E'},
         'I': {'G'},
         'K': {'I'}}

g1 = nx.DiGraph()
g1.add_nodes_from(['B', 'F', 'G', 'D', 's0', 'e0'])
g1.add_edges_from([('F', 'B'), ('D', 'F'), ('G', 'F'), ('e0', 'G'), ('e0', 'D'), ('B', 's0')])

g2 = nx.DiGraph()
g2.add_nodes_from(['B', 'A', 'D', 'C', 'E', 's1', 'e1'])
g2.add_edges_from([('B', 'A'), ('C', 'A'), ('D', 'B'), ('D', 'C'), ('E', 'D'), ('e1', 'E'), ('A', 's1')])

g4 = nx.DiGraph()
g4.add_nodes_from(['s0', 'A', 'B', 'C', 'D', 'E', 'F', 'e0'])
g4.add_edges_from([('A', 's0'), ('A', 'B'), ('B', 'C'), ('B', 'D'), ('E', 'A'), ('F', 'A'), ('e0', 'E'), ('e0', 'F')])

g5 = nx.DiGraph()
g5.add_nodes_from(['s0', 'A', 'B', 'C', 'K', 'e0'])
g5.add_edges_from([('A', 's0'), ('B', 'A'), ('C', 'A'), ('K', 'B'),  ('e0', 'K'), ('K', 'C'), ('e0', 'B'), ('e0', 'C')])


def make_flow_graph(recipes, start_nodes):
    sorted_recipes = []
    for r, i in zip(recipes, range(len(recipes))):
        sr = kahn_topological_sort(r, start_nodes[i])
        sorted_recipes.append(sr)

    g = nx.DiGraph()

    for r in sorted_recipes:
        g.add_nodes_from(r)
        g_temp = nx.DiGraph()
        g_temp.add_nodes_from(r)
        g_temp.add_path(r)
        g = nx.compose(g, g_temp)

    return g


def kahn_topological_sort(graph, start_node):
    L = []
    S = {n for n in graph.nodes() if not graph.successors(n)}
    first = True
    while S:
        if first:
            n = start_node
            S.remove(n)
            first = False
        else:
            n = S.pop()
        L += [n]
        for m in [m for m, x in graph.edges() if x == n]:
            graph.remove_edge(m, n)
            if not graph.successors(m):
                S.add(m)
    x = graph.edges()
    if x:
        raise ValueError('Graph has at least one cycle')
    else:
        return L

pos1 = layout.spring_layout(g1, iterations=50)
nx.draw(g1, pos=pos1)
nx.draw_networkx_labels(g1, pos=pos1)
plt.show()

pos2 = layout.spring_layout(g2, iterations=50)
nx.draw(g2, pos=pos2)
nx.draw_networkx_labels(g2, pos=pos2)
plt.show()

g = make_flow_graph([g1, g2], ['s0', 's1'])
pos = layout.spring_layout(g, iterations=50)
nx.draw(g, pos=pos)
nx.draw_networkx_labels(g, pos=pos)
plt.show()