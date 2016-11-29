import networkx as nx
import matplotlib.pyplot as plt
from collections import OrderedDict

class Recipe:
    def __init__(self, dependencies, start_module, start_direction):
        self.dependencies = dependencies
        self.start_module = start_module
        self.start_direction = start_direction

    def __getitem__(self, item):
        return self.dependencies[item]

    def values(self):
        return self.dependencies.values()

    def keys(self):
        return self.dependencies.keys()

    def items(self):
        return self.dependencies.items()

    def __len__(self):
        return len(self.dependencies)

    def to_DiGraph(self):
        # TODO: Dunno om det her virker
        G = nx.DiGraph()
        nodes = {item for sublist in self.values() for item in sublist}
        nodes |= set(self.keys())
        G.add_nodes_from(nodes)
        for item in self.items():
            for dependency in item[1]:
                G.add_edge(item[0], dependency)
        return G

    def to_topological_sorted_DiGraph(self):
        return self.kahn_topological_sort(self.to_DiGraph(), self.start_module)


    @staticmethod
    def get_flow_graph(recipes):
        G = nx.DiGraph()
        sorted_recipes = []
        for r in recipes:
            sr = r.to_topological_sorted_DiGraph()
            sorted_recipes.append(sr)

        for r in sorted_recipes:
            G.add_nodes_from(r)
            temp = nx.DiGraph()
            temp.add_nodes_from(r)
            temp.add_path(r)
            G = nx.compose(G, temp)

        return G

    @staticmethod
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
            G = nx.DiGraph()
            G.add_nodes_from(L)
            for i in range(1, len(L)):
                G.add_edge(L[i], L[i - 1])
            return G

    @staticmethod
    def plot(G):
        pos1 = nx.layout.spring_layout(G, iterations=50)
        nx.draw(G, pos=pos1)
        nx.draw_networkx_labels(G, pos=pos1)
        plt.show()


func_deps0 = {0: set(), 1: {0}, 2: {0}, 3: {1, 2}, 4: {3}, 5: {3}}
func_deps1 = {6: set(), 0: {6}, 1: {0}, 2: {1}, 3: {1}, 4: {1}, 5: {4}, 8: {3}, 7: {4}}

func_deps = OrderedDict()
func_deps[0] = set()
func_deps[2] = {0}
func_deps[3] = {2}
func_deps[6] = {3}
func_deps[7] = {6}

func_deps2 = {0: set(), 1: {0}, 4: {1}, 6: {4}, 7: {6}}
func_deps3 = {0: set(), 2: {0}, 5: {2}, 6: {5}, 7: {6}}

r0 = Recipe(func_deps, 0, 3)
r1 = Recipe(func_deps2, 0, 3)
r2 = Recipe(func_deps3, 0, 3)

G = Recipe.get_flow_graph([r0, r1, r2])
pos1 = nx.layout.spring_layout(G, iterations=50)
nx.draw(G, pos=pos1)
nx.draw_networkx_labels(G, pos=pos1)
plt.show()