from module import SquareModule

def create_transporters(amount, time, queue_size):
    transporters = []
    for i in range(amount):
        t = SquareModule('trans_' + str(i), [], {}, time, queue_size, allow_passthrough= True)
        transporters.append(t)
    return transporters



def get_factorial_list(nodes):
    n = []
    for i in range(1, len(nodes) + 1):
        n.append({x for j, x in enumerate(nodes) if j < i})

    return n

def initial_configuration(recipes, modules, transporters=None):
    G = Recipe.get_flow_graph(recipes)
    G.reverse()
    G_copy = nx.topological_sort(G)

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

        smallest_len = len(G)
        candidate = None
        for m in current:
            if len(m.w_type) <= smallest_len:
                smallest_len = len(m.w_type)
                candidate = m

        candidate.active_w_type = set(G_copy[:size])
        conf.append(candidate)
        G_copy = G_copy[size:]

    for i, m in enumerate(conf):
        if i < len(conf) - 1:
            m.right = conf[i + 1]

    return conf