from module import SquareModule
from recipe import Recipe
from configuration.tabu_search import tabu_search, get_travsersal_info


def get_top_nodes(G):
     top_nodes = []
     for node in G:
          no_preds = True
          predecessors = G.predecessors_iter(node)

          for n in predecessors:
               no_preds = False
               break

          if no_preds:
               top_nodes.append(node)

     return top_nodes


def initial_configurations(G, modules, setup):
    G_copy = G.copy()
    top_nodes = []

    # If a setup is already given, remove as many top nodes as possible
    if setup:
        flag = True  # Flag tells if we may remove more top nodes
        while flag:
            flag = False
            top_nodes = get_top_nodes(G_copy)
            for node in top_nodes:
                if node in setup[-1].w_type:
                    G_copy.remove_node(node)
                    flag = True
    # If setup is empty just get the top nodes
    else:
        top_nodes = get_top_nodes(G_copy)

    results = []
    if not G_copy:
        results.append(setup)
    else:
        for node in top_nodes:
            mods = [m for m in modules if node in m.w_type]
            for m in mods:
                update_mods = modules.copy()
                update_mods.remove(m)
                new_setup = setup + [m]
                results = results + (initial_configurations(G_copy, update_mods, new_setup))
    return results


t = [[0, 0, 0, 0],
     [0, 0, 0, 0],
     [0, 0, 0, 0],
     [0, 0, 0, 0]]

m0 = SquareModule('hammer-maskine', {'hammer': 10, 'mere hammer': 10}, t, 3)

m1 = SquareModule('skrue-maskine', {'skrue': 10}, t, 3)

m2 = SquareModule('pakke-maskine', {'pakke': 10}, t, 3)

m0.active_w_type = {'hammer', 'mere hammer'}
m1.active_w_type = {'skrue'}
m2.active_w_type = {'pakke'}

m3 = SquareModule('super-skruer', {'skrue': 4}, t, 3)
m4 = SquareModule('super-pakker', {'pakke': 2}, t, 3)


m0.up = m1
m1.up = m2

r0 = Recipe('chokolade', {'hammer': set(), 'mere hammer': {'hammer'}, 'skrue': {'mere hammer'}, 'pakke': {'skrue'}}, 'hammer-maskine', 0, 2)

G = r0.to_DiGraph().reverse()
print(initial_configurations(G, [m0,m1,m2, m3, m4], []))




#res = tabu_search([r0], [m0, m1, m2, m3, m4], (lambda r, m, t: [m0, m1, m2]))
#print(res)


#worked_on, transported_through = get_travsersal_info("../experiments/Output.txt", m_map, r_map)

#print(worked_on)
#print(transported_through)