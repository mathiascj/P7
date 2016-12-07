from module import SquareModule
from recipe import Recipe
from configuration.tabu_search import tabu_search
from UPPAAL.uppaalAPI import get_best_time
from networkx import nx
from random import shuffle

VERIFYTA = '../UPPAAL/verifyta'
XML_TEMPLATE = "../../Modeler/iter3.4.1.xml"

def get_top_nodes(G):
    """
    Finds all nodes with no successors
    :param G: a nx Digraph
    :return: a list of tuples, each tuple containing node name and node attribute dict
    """
    top_nodes = []
    for node in G.nodes(data=True):
        if not G.successors(node[0]):
            top_nodes.append(node)

    return top_nodes


# THIS IS THE POLICE SPEAKING
# THIS IS A GENERATOR NOT A FUNCTION, BE WARY CITIZEN
def initial_configurations(G, modules, setup, recipe_starters, active_works):
    """
    If possible creates a linear configuration.
    :param G: Graph describing recipes
    :param modules: modules which may be placed
    :param setup:  linear configuration setup up till now
    :param recipe_starters: dict describing which module each recipe starts at
    :param active_works: dict describing what works a module performs
    :param branches: A list, where each element is a list of arguments,
           which called on this function lets us explore a new branch
    :return:  Empty list if no branches are left

    """

    # Creates copies to get around referential integrity :-)
    G_copy = G.copy()
    recipe_starters_copy = recipe_starters.copy()
    active_works_copy = active_works.copy()

    # If a setup is already given, remove as many top nodes as possible
    top_nodes = []
    if setup:
        flag = True  # Flag tells if we may remove more top nodes
        while flag:
            flag = False
            current_module = setup[-1]
            top_nodes = get_top_nodes(G_copy)
            for node in top_nodes:
                work = node[0]
                starts = node[1]['starts']

                #  If the top node is workable by the current module it is removed
                if work in current_module.w_type:
                    flag = True
                    G_copy.remove_node(work)

                    # Updates recipe_starters dict, if a recipe should start at current_module
                    for start in starts:
                        if start not in recipe_starters_copy:
                            recipe_starters_copy[start] = current_module

                    # Updates active_works for current module with the removed top node
                    if current_module not in active_works_copy:
                        active_works_copy[current_module] = set()
                    active_works_copy[current_module].add(work)

    # If setup is empty just get the top nodes
    else:
        top_nodes = get_top_nodes(G_copy)

    new_branches = []

    # If graph is empty we yield the setup
    if not G_copy:
        yield G_copy, modules, setup, recipe_starters_copy, active_works_copy

    # If graph is not empty we try placing new modules.
    else:
        for node in top_nodes:
            work = node[0]
            mods = [m for m in modules if work in m.w_type]
            shuffle(mods) # Makes sure we yield random branches
            # Places down a module and constructs a new branch from this choice
            for m in mods:
                update_mods = modules.copy()
                update_mods.remove(m)
                new_setup = setup + [m]
                yield from initial_configurations(G_copy, update_mods, new_setup, recipe_starters_copy, active_works_copy)



def recipes_to_graph(recipes):
    """
    Given a list of recipes, will create a func dep graph for each which it will then compose.
    :param recipes: A list of recipe object
    :return: A combined graph where the 'starts' attribute for each node has been set
    """
    result_graph = nx.DiGraph()

    for r in recipes:
        # Turn recipe to graph and get top nodes
        r_graph = r.to_DiGraph()
        top_nodes = get_top_nodes(r_graph)
        top_nodes = [x[0] for x in top_nodes]  # Get only names of nodes not attributes

        # Iterate over each node in graph
        for node in r_graph.nodes(data = True):
            work = node[0]
            attributes = node[1]

            # If node is a top node, it has its starts attribute set to the recipe name
            attributes['starts'] = set()
            if work in top_nodes:
                attributes['starts'].add(r.name)

                # If this node is already in the result_graph we store elements from its start attributes
                # in the r_graph node, as to retain it after compose.
                if work in result_graph:
                    res_set = result_graph.node[work]['starts']
                    attributes['starts'].update(res_set)

        # Attributes of r_graph take presedence over result_graph's
        result_graph = nx.compose(result_graph, r_graph)

    return result_graph

t = [[0, 0, 0, 0],
     [0, 0, 0, 0],
     [0, 0, 0, 0],
     [0, 0, 0, 0]]

m0 = SquareModule('hammer-maskine', {'hammer': 10, 'mere hammer': 10}, t, 3)

m1 = SquareModule('skrue-maskine', {'skrue': 10}, t, 3)

m2 = SquareModule('pakke-maskine', {'pakke': 10}, t, 3)

m6 = SquareModule('Smadremanden', {'smadre': 10}, t, 3)

m0.active_w_type = {'hammer', 'mere hammer'}
m1.active_w_type = {'skrue'}
m2.active_w_type = {'pakke'}

m3 = SquareModule('super-skruer', {'skrue': 4}, t, 3)
m4 = SquareModule('super-pakker', {'pakke': 2}, t, 3)

m6 = SquareModule('smadre-manden', {'smadre': 50}, t, 3)

r0 = Recipe('chokolade', {'hammer': set(), 'mere hammer': {'hammer'}, 'skrue': {'mere hammer'}, 'pakke': {'skrue'}}, 'hammer-maskine', 0, 2)
r1 = Recipe('FuckMigUp', {'smadre': set()}, 'balh', 0, 2)

G = recipes_to_graph([r0, r1])
args = [G, [m0,m1,m2, m3, m4, m6], [], {}, {}]

counter = 0
gener = initial_configurations(*args)
while counter < 16:
    print(gener.__next__())
    counter += 1





#
# counter = 0
# while counter < 16 and flag:
#     res = initial_configurations(*args)
#
#     if res:
#         print(res[0][2])
#         counter += 1
#         branches = res[-1]
#         if branches:
#             branch = choice(branches)
#             branches.remove(branch)
#             branch.append(branches)
#             args = branch
#         else:
#             flag = False
#     else:
#         flag = False
#
# if not flag:
#     print("Nut enuff gov")

# init_time,worked_on, transported_through = get_best_time([r0], confs[2], XML_TEMPLATE, VERIFYTA)
# print(init_time)


#res = tabu_search([r0], [m0, m1, m2, m3, m4], (lambda r, m, t: confs[3]))
#print(res)


#worked_on, transported_through = get_travsersal_info("../experiments/Output.txt", m_map, r_map)

#print(worked_on)
#print(transported_through)