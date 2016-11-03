from module import *

def get_set_of_work_types(modules):
    S = set()
    for m in modules:
        S.add(m.w_type)
    return S


def make_linear_configuration(flow_graph, modules):
    fg_wt = set(flow_graph.nodes())
    m_wt = get_set_of_work_types(modules)
    if fg_wt != m_wt:
        raise ValueError('The Flow graph and the Modules does not contain the same work types')

