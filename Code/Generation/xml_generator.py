from xml.etree.ElementTree import parse
from copy import deepcopy
from collections import OrderedDict
from  module import Module


def create_model_xml(file, global_decl_string, recipe_strings, system_string, new_file):
    """
    Updates base UPPAAL xml file using input strings as replacement
    :param file: Path to base file
    :param global_decl_string: String to replace global declaration
    :param recipe_strings: String to create new recipe templates
    :param system_string: String to replace system
    :param new_file: Path to new file
    """
    tree = parse(file)

    # Update text in the global declaration
    global_decl = tree.find("declaration")
    global_decl.text = global_decl_string

    # Find recipe template node
    templates = tree.findall("template")
    for t in templates:
        if t.find("name").text == "Recipe":
            recipe_template = t
            break

    # Remove both recipe template and system nodes
    tree.getroot().remove(recipe_template)
    system_decl = tree.find("system")
    tree.getroot().remove(system_decl)

    # For each set of recipe strings, creates a new recipe template with a unique name and parameters.
    # We need a unique recipe template for each recipe, as the sizes of arrays declared as parameters
    # statically depend on recipe size.
    for r in recipe_strings:
        temp_copy = deepcopy(recipe_template)

        n = temp_copy.find("name")
        n.text = r["name"]

        p = temp_copy.find("parameter")
        p.text = r["parameter"]

        tree.getroot().append(temp_copy)

    # Creates a new system node and adds it
    system_decl.text = system_string
    tree.getroot().append(system_decl)

    tree.write(new_file)


def generate_xml(template_file, modules, recipes, new_file_name="test.xml"):
    """
    Method to be called directly by user.
    Based on modules and recipes a new UPPAAL model is formed.
    :param template_file: Path to base UPPAAL file of the model
    :param modules: A list of FESTO modules
    :param recipes: A list of recipes, each being a functional dependency graph
    :param new_file_name: Path to new file
    """

    # Finds number of unique worktypes that can be performed with the modules
    S = set()
    for m in modules:
        S.add(m.work_type)
    number_of_worktypes = len(S)

    # Generation of global string
    global_decl_string = generate_global_declarations(len(modules), number_of_worktypes, recipes)

    # Generation of recipe strings, to be used to create new templates
    recipe_strings = generate_recipe_templates(len(recipes))

    # Generation of system string
    system_string = generate_module_declarations(modules)

    for id, r in enumerate(recipes):
        system_string += generate_recipe_declaration(id, r)

    system_string += "rem = Remover();\n"
    system_string += "cos = Coster(1);\n"
    system_string += generate_system_declaration(len(modules), len(recipes))
    # TODO generate different connections for the modules and make an xml file for each
    create_model_xml(template_file, global_decl_string, recipe_strings, system_string, new_file_name)


def generate_global_declarations(number_of_modules, number_of_worktypes, recipes):
    """
    Generates a string to replace text in global declaration node
    :param number_of_modules: Number of modules in model
    :param number_of_worktypes: Number of unique work types
    :param recipes: Recipies to be performed on model
    :return global declaration string
    """
    s = "const int NUMBER_OF_MODULES = " + str(number_of_modules) + ";\n"
    s += "const int NUMBER_OF_WORKTYPES = " + str(number_of_worktypes) + ";\n"
    s += "const int NUMBER_OF_RECIPES = " + str(len(recipes)) + ";\n"

    # Creates a size contant for each recipe
    for id, r in enumerate(recipes):
        s += "const int N_OF_NOD" + str(id) + " = " + str(len(r)) + ";\n"

    s += """chan transport[NUMBER_OF_MODULES + 1];
chan work[NUMBER_OF_WORKTYPES + 1];
chan handshake[NUMBER_OF_RECIPES + 1];

clock global_c;

typedef int[-1, NUMBER_OF_RECIPES] rid_t;
typedef int[0, NUMBER_OF_WORKTYPES] wid_t;
typedef int[0, NUMBER_OF_MODULES] id_t;

rid_t var = 0;

meta int remaining = 0;
"""

    return s


def generate_recipe_templates(number_of_recipes):
    """
    Generates a list of dictionaries. Each used to generate a unique Recipe template.
    :param number_of_recipes: number of total recipes
    :return: list of dicts to generate recipe templates
    """
    recipe_string_list = []

    # For each recipe, generates a dict
    for r in range(number_of_recipes):
        recipe_string = {}

        recipe_string["name"] = "Recipe" + str(r)

        recipe_string["parameter"] = \
            "rid_t rid, wid_t& n_work[N_OF_NOD" + str(r) + \
            "],  int& n_num_parents[N_OF_NOD" + str(r) + \
            "], int& n_children[N_OF_NOD" + str(r) + \
            "][N_OF_NOD" + str(r) + \
            "], int& n_children_len[N_OF_NOD" + str(r) + "]"

        recipe_string_list.append(recipe_string)

    return recipe_string_list


def generate_recipe_declaration(id, recipe):
    """
    Generates the part of system that declares new recipes
    :param id: ID of recipes, should match with it's size constant N_OF_NOD
    :param recipe: a functional dependency graph
    :return: string to declare a recipe in system
    """

    number_of_nodes = len(recipe)
    size = "N_OF_NOD" + str(id)
    n_works = []
    n_num_parents = []
    n_children = []
    n_children_len = []

    # For each node add information to the initialization lists
    for work, deps in recipe.items():
        n_works.append(work)
        n_num_parents.append(len(deps))
        children = []

        for node_id, parents in enumerate(recipe.values()):
            if work in parents:
                children.append(str(node_id))

        n_children_len.append(len(children))

        # Fills out rest of list with -1s
        while len(children) < number_of_nodes:
            children.append(-1)

        n_children.append("{" + ",".join(map(str,children)) + "}")

    # Creates actual declaration string
    s = ""
    s += "wid_t n_works" + str(id) + "[" + size + "] = {" + ",".join(map(str,n_works)) + "};\n"
    s += "int num_parents" + str(id) + " [" + size + "] = {" + ",".join(map(str,n_num_parents)) + "};\n"
    s += "int num_children" + str(id) + " [" + size + "][" + size + "] = {" + ",".join(map(str, n_children)) + "};\n"
    s += "int n_children_len" + str(id) + "[" + size + "] = {" + ",".join(map(str, n_children_len)) + "};\n"
    s += "r" + str(id) +\
         " = Recipe(" + str(id) + ", n_works, n_num_parents, n_children, n_children_len," + size + ");\n"

    return s

def generate_module_declarations(modules): #TODO update this to fit new modules!

    s = ""
    for module in modules:  # Define connections
        s += "int connections" + str(module.module_id) + "[4] = {"  # TODO a module has a maximum of 4 connections
        for index in module.get_connections():
            s += str(index) + ", "

        for i in range(0, 4 - len(module.get_connections())):
            s += "-1, "

        s = s[:-2]  # remove last comma and space, added in loop
        s += "};\n"

    s += "\n"
    for module in modules:  # Define processes
        s += "m" + str(module.module_id) + \
             " = Module(" + str(module.module_id) + \
             ", " + str(module.work_type) + \
             ", " + str(module.processing_time) + \
             ", " + str(module.transport_time) + \
             ", " + str(module.cost_rate) + \
             ", " + "connections" + str(module.module_id) + \
             ", " + str(module.num_of_connections) + ");\n"

    s += "\n\n"
    return s


def generate_system_declaration(number_of_modules, number_of_recipes):
    """
    To system declaration, generates a string including all modules and recipes
    :param number_of_modules: total number of FESTO modules
    :param number_of_recipes: total number of recipes
    :return: string to add all recipes and modules to system
    """
    s = "system rem, cos"
    for i in range(number_of_modules):  # add processes/modules to system definition
        s += ", m" + str(i + 1)

    for i in range(number_of_recipes):
        s += ", r" + str(i + 1)

    s += ";"
    return s


def generate_query(number_of_recipes, new_file_name="test.q"):
    """
    Generates a query file, containing a query to check whether all recipes are done.
    :param number_of_recipes: total number of recipes
    :param new_file_name: path to new file
    """
    s = "E<> "
    for i in range(number_of_recipes):
        if i + 1 != 1:
            s += " && "
        s += "r" + str(i + 1) + ".done"
    f = open(new_file_name, 'w')
    f.write(s)
    f.close()

"""
func_deps = OrderedDict()
func_deps[3] = set([2,4])
func_deps[2] = set([1])
func_deps[4] = set([1])
func_deps[1] = set([])

dunc_feps = OrderedDict()
dunc_feps[3] = set([2,4])


m1 = Module(1,1,5,3,2,set([2,3]))
m2 = Module(2,2,5,3,2,set([4]))
m3 = Module(3,4,5,3,2,set([4]))
m4 = Module(4,3,5,3,2,set([]))

generate_xml("../../Modeler/iter2.xml", [m1,m2,m3,m4], [func_deps, dunc_feps])
"""