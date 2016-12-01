from UPPAAL.verifytaAPI import run_verifyta, get_trace_time, pprint
from Generation.xml_generator import generate_xml

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
    generate_xml(template_file=template_file, modules=modules, recipes=recipes, xml_name=XML_FILE, q_name=Q_FILE)
    result, trace = run_verifyta(XML_FILE, Q_FILE, "-t 2 -o 3", verifyta=verifyta)
    time = get_trace_time(trace)
    return time