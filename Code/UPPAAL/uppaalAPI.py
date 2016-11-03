import verifytaAPI
from xml_generator import generate_xml, generate_query

NEW_XML_FILE = 'temp.xml'
NEW_Q_FILE = 'temp.q'
DEFAULT_COST = 0


def xml_helper(configuration, modules, recipes, template_file):
    """
    Generates the XML and Q file for a given configuration, modules and recipes
    SIDE EFFECT: Changes the connections in each module
    SIDE EFFECT: Overrides NEW_XML_FILE and NEW_Q_FILE files
    :param configuration: A configuraion of modules
    :param modules: A list of modules
    :param recipes: A list of recipes
    :param template_file: A path to a template UPPAAL CORA XML file
    """
    for m in modules:
        m.set_connections(configuration)
    generate_xml(template_file=template_file, modules=modules, recipes=recipes, new_file_name=NEW_XML_FILE)
    generate_query(len(recipes), NEW_Q_FILE)


def get_best_cost(configuration, modules, recipes, template_file, verifyta):
    """
    Gets the best cost of a given configuration, modules and recipes
    :param configuration: A configuraion of modules
    :param modules: A list of modules
    :param recipes: A list of recipes
    :param template_file: A path to a template UPPAAL CORA XML file
    :param verifyta: A path to an instance of UPPAAL CORAs verifyta
    :return: The best cost of the configuration
    """
    xml_helper(configuration, modules, recipes, template_file)  # Has side effects
    result, trace = verifytaAPI.run_verifyta_best_randbestdepth(xml=NEW_XML_FILE, queries=NEW_Q_FILE, verifyta=verifyta)
    cost = verifytaAPI.get_best_cost(trace, DEFAULT_COST)
    return cost


def get_satisfies_recipes(configuration, modules, recipes, template_file, verifyta):
    """
    Checks if a configuration can satisfy the recipes
    :param configuration: A configuraion of modules
    :param modules: A list of modules
    :param recipes: A list of recipes
    :param template_file: A path to a template UPPAAL CORA XML file
    :param verifyta: A path to an instance of UPPAAL CORAs verifyta
    :return: Boolean, whether or not the given configuration can satisfy the recipes
    """
    xml_helper(configuration, modules, recipes, template_file)  # Has side effects
    result, trace = verifytaAPI.run_verifyta_some_breadth(NEW_XML_FILE, NEW_Q_FILE, verifyta)
    satisfied = verifytaAPI.get_satisfied(result)
    return satisfied