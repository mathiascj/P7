from UPPAAL.verifytaAPI import run_verifyta, get_trace_time, pprint
from UPPAAL.xml_generator import generate_xml
import re

XML_FILE = 'temp.xml'
Q_FILE = 'temp.q'


def get_best_time(recipes, modules, template_file, verifyta):
    """
    Gets the best cost of a given configuration, modules and recipes
    :param configuration: A configuraion of modules
    :param modules: A list of modules
    :param recipes: A list of recipes
    :param template_file: A path to a template UPPAAL CORA XML file
    :param verifyta: A path to an instance of UPPAAL CORAs verifyta
    :return: The best cost of the configuration
    """
    m_map, w_map, r_map =\
        generate_xml(template_file=template_file, modules=modules, recipes=recipes, xml_name=XML_FILE, q_name=Q_FILE)
    result, trace = run_verifyta(XML_FILE, Q_FILE, "-t 2", "-o 3", "-u", "-y", verifyta=verifyta)

    time = get_trace_time(trace)

    trace_iter = iter((trace.decode('utf-8')).splitlines())
    worked_on, transported_through = get_travsersal_info(trace_iter, m_map, r_map)

    return time, worked_on, transported_through


def get_travsersal_info(trace_iter, module_map, recipe_map):
    """
    :param trace_iter: An iterator to run over lines in trace output
    :param module_map: A mapping from UPPAAL m_ids to the originals
    :param recipe_map: A mapping from UPPAAL r_ids to the originals
    :return: worked on: dict telling us for each module, what recipe types have been worked by it
             transported_through: dict telling us for each module, what recipe types have been transorted through it.
    """

    worked_on = {}
    transported_through = {}

    for line in trace_iter:
        if line == "Transitions:":
                lines = []
                counter = 0

                # Get the two lines describing the transition
                for line in trace_iter:
                    lines.append(line)
                    counter += 1
                    if counter == 2:
                        break

                # If the transition is a handshake. Work is being performed.
                if "handshake" in lines[0]:
                    r_id = int(re.findall("\d+", lines[0])[0])

                    m_id = int(re.findall("\d+", lines[1])[0])
                    m_id = module_map[m_id]

                    if m_id not in worked_on:
                        worked_on[m_id] = set()

                    # Adds recipe type to the given module
                    worked_on[m_id].add((recipe_map[r_id]))

                # If the transition is an enqueue using a transporter. Transportation is being performed.
                elif "enqueue" in lines[0] and "mtransporter" in lines[0]:
                    m_id = int(re.findall("\d+", lines[0])[0])
                    m_id = module_map[m_id]

                    # Gets the line describing the state after transition
                    state_line = ""
                    counter = 0
                    for line in trace_iter:
                        counter += 1
                        if counter == 5:
                            state_line = line
                            break

                    # Gets the id of the recipe, lying in the global var
                    r_id = int(re.findall("var=(\d+)", state_line)[0])

                    if m_id not in transported_through:
                        transported_through[m_id] = set()

                    # Adds recipe type to the given module
                    transported_through[m_id].add(recipe_map[r_id])


    return worked_on, transported_through