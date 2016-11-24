from xml.etree.ElementTree import parse
from copy import deepcopy
from collections import OrderedDict
from framework.module import SquareModule
from framework.recipe import Recipe

# GLOBALS DECLS
# String decls put here for the sake of easier reconfiguration
STR_NUMBER_OF_MODULES = "NUMBER_OF_MODULES"
STR_NUMBER_OF_RECIPES = "NUMBER_OF_RECIPES"
STR_NUMBER_OF_WORKTYPES = "NUMBER_OF_WORKTYPES"
STR_NUMBER_OF_OUTPUTS = "NUMBER_OF_OUTPUTS"
STR_NUMBER_OF_INITS = "NUMBER_OF_INITS"

STR_MID = "mid"     # Module ID
STR_RID = "rid"     # Recipe ID
STR_WID = "wid"     # Worktype ID
STR_DID = "did"     # Direction ID

STR_WA = "work_array"
STR_PA = "ptime_array"
STR_CA = "crate_array"
STR_NA = "next_array"
STR_TA = "ttime_array"


STR_MODULE_QUEUE = "mqueue"
STR_MODULE_WORKER = "mworker"
STR_MODULE_TRANSPORTER = "mtransporter"

STR_RECIPE_NAME = "recipe"


def const_int_decl(variable_name, init_value):
    """
    :param variable_name: Name of the variable
    :param init_value: Value that the variable be instantiated to
    :return: A const int declaration
    """
    return "const " + int_decl(variable_name, init_value)


def int_decl(variable_name, init_value=""):
    """
    :param variable_name: Name of the variable
    :param init_value: Value that the variable be instantiated to
    :return: A int declaration
    """
    s = "int " + variable_name
    if init_value:
        s += " = " + str(init_value)
    s += ";\n"
    return s


def typedef_decl(type_name, max_val):
    """
    :param type_name: The name of the new type, will be appended with _t and _safe_t
    :param max_val: The maximum value of the new type minus one
    :return: A string declaring a two types, an unsafe and a safe one.
    """
    s = "typedef int[-1, " + str(max_val) + " - 1] " + type_name + "_t;\n"
    s += "typedef int[0, " + str(max_val) + " - 1] " + type_name + "_safe_t;\n"
    return s


def chan_decl(chan_name, size, urgent=False):
    """
    :param chan_name: Name of the channel
    :param size: Size of the channel
    :param urgent: Bool if the channel should be urgent
    :return: A string that declare the channel
    """
    s = ""
    if urgent:
        s += "urgent "
    return s + "chan " + chan_name + "[" + str(size) + "];\n"


def create_model_xml(file, global_decl_string, system_string, new_file):
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

    # Remove system nodes
    system_decl = tree.find("system")
    tree.getroot().remove(system_decl)


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
        S.update(m.w_type)
    number_of_worktypes = len(S)

    # Generation of global string
    global_decl_string = generate_global_declarations(len(modules), len(recipes), number_of_worktypes, 4)

    # Generation of system string
    system_string = ""
    system_list =  []
    for m in modules:
        q, w, t, s = generate_module_declaration(m, number_of_worktypes, 4)
        system_string += s
        system_list.append(q)
        system_list.append(w)
        system_list.append(t)

    recipe_names = []

    for id, r in enumerate(recipes):
        r, s = generate_recipe_declaration(id, r, number_of_worktypes)
        system_string += s
        recipe_names.append(r)

    system_string += "rid_t rqa[" + STR_NUMBER_OF_RECIPES + "]" + " = {"
    for id, r in enumerate(recipes):
        system_string += str(id)
        if id < len(recipes) - 1:
            system_string += ", "
    system_string += "};\n"

    system_string += "rqueue = RecipeQueue(rqa);"
    system_list.append("rqueue")




    system_string += "rem = Remover();\n"
    system_string += "cos = Coster(1);\n"
    system_list.append("rem")
    system_list.append("cos")

    system_string += generate_system_declaration(system_list + recipe_names)
    # TODO generate different connections for the modules and make an xml file for each
    create_model_xml(template_file, global_decl_string,  system_string, new_file_name)
    create_query(recipe_names)


def generate_global_declarations(number_of_modules, number_of_recipes, number_of_worktypes, number_of_outputs,
                                 number_of_inits):
    """
    Generates a string to replace text in global declaration node
    :param number_of_modules: Number of modules in model
    :param number_of_worktypes: Number of unique work types
    :param number_of_recipes: Number of recipes
    :return global declaration string
    """
    s = "// Global Declarations\n"

    # Constants
    s += "// Constants\n"
    s += const_int_decl(STR_NUMBER_OF_MODULES, number_of_modules)
    s += const_int_decl(STR_NUMBER_OF_RECIPES, number_of_recipes)
    s += const_int_decl(STR_NUMBER_OF_WORKTYPES, number_of_worktypes)
    s += const_int_decl(STR_NUMBER_OF_OUTPUTS, number_of_outputs)
    s += const_int_decl(STR_NUMBER_OF_INITS, number_of_inits)
    s += "\n"

    # Types
    s += "// User defined types.\n"
    s += "// Safe means that we cannot go to -1.\n"
    s += "// -1 is however sometimes needed as a filler value, so it can be permitted.\n"
    s += typedef_decl(STR_MID, STR_NUMBER_OF_MODULES)
    s += typedef_decl(STR_RID, STR_NUMBER_OF_RECIPES)
    s += typedef_decl(STR_WID, STR_NUMBER_OF_WORKTYPES)
    s += typedef_decl(STR_DID, STR_NUMBER_OF_OUTPUTS)
    s += "\n"

    # Channels
    s += "// Channels\n"
    s += chan_decl("enqueue", STR_NUMBER_OF_MODULES, True)
    s += chan_decl("work_dequeue", STR_NUMBER_OF_MODULES)
    s += chan_decl("transport_dequeue", STR_NUMBER_OF_MODULES)
    s += chan_decl("intern", STR_NUMBER_OF_MODULES, True) 
    s += chan_decl("remove", STR_NUMBER_OF_RECIPES)
    s += chan_decl("rstart", STR_NUMBER_OF_RECIPES)
    s += chan_decl("handshake", STR_NUMBER_OF_RECIPES)
    s += chan_decl("work", STR_NUMBER_OF_WORKTYPES)
    s += chan_decl("initialize", STR_NUMBER_OF_INITS)
    s += "urgent chan urg;\n"
    s += "\n"

    # Misc
    s += "// Global clock and remaining heuristic\n"
    s += "clock global_c;\n"
    s += "meta int remaining;\n"
    s += "\n"

    s += "// Variables for communicating values\n"
    s += int_decl("var")
    s += int_decl("var2")

    s += """
//Variables used for passing values at handshake
int var = -1;
int var2 = -1;
bool can_continue = true;
bool can_add_recipe = true;

//Functions for tracking completed recipes
bool ra_done[NUMBER_OF_RECIPES];

void init_ra_done(){
    int i;
    for(i = 0; i < NUMBER_OF_RECIPES; ++i)
        ra_done[i] = false;
}

bool is_done(rid_safe_t rid){
    return ra_done[rid];
}


bool current_works[NUMBER_OF_RECIPES][NUMBER_OF_WORKTYPES];

void init_current_works(){
    int i, j;
    for(i = 0; i < NUMBER_OF_RECIPES; ++i)
        for(j = 0; j < NUMBER_OF_WORKTYPES; ++j)
            current_works[i][j] = false;
}


bool can_work(bool worktype[NUMBER_OF_WORKTYPES], rid_safe_t rid){
    int i;
    for(i = 0; i < NUMBER_OF_WORKTYPES; ++i){
        if(worktype[i] &&  current_works[rid][i])
            return true;}
    return false;
}

bool full_modules[NUMBER_OF_MODULES];
bool idle_workers[NUMBER_OF_MODULES];
bool idle_transporters[NUMBER_OF_MODULES];
"""
    return s


def generate_recipe_declaration(id, recipe, number_of_worktypes):
    """
    Generates the part of system that declares new recipes
    :param id: ID of recipes, should match with it's size constant N_OF_NOD
    :param recipe: a functional dependency graph
    :return: string to declare a recipe in system
    """

    number_of_nodes = len(recipe)
    size = STR_NUMBER_OF_WORKTYPES
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

        filler = children.copy()
        while len(filler) < number_of_worktypes:
            filler.append(-1)
        n_children.append("{" + ", ".join(map(str, filler)) + "}")

    # Creates actual declaration string
    varname = STR_RECIPE_NAME + str(id)

    s = "// Recipe " + str(id) + "\n"

    filler = n_works.copy()
    while len(filler) < number_of_worktypes:
        filler.append(-1)
    s += "wid_t n_works" + str(id) + "[" + size + "] = {" + ", ".join(map(str, filler)) + "};\n"

    filler = n_num_parents.copy()
    while len(filler) < number_of_worktypes:
        filler.append(-1)
    s += "int num_parents" + str(id) + " [" + size + "] = {" + ", ".join(map(str, filler)) + "};\n"

    filler = n_children.copy()
    while len(filler) < number_of_worktypes:
        filler.append("{" + ", ".join(map(str, [-1] * number_of_worktypes)) + "}")
    s += "int num_children" + str(id) + " [" + size + "][" + size + "] = {" + ", ".join(map(str, filler)) + "};\n"

    filler = n_children_len.copy()
    while len(filler) < number_of_worktypes:
        filler.append(-1)
    s += "int n_children_len" + str(id) + "[" + size + "] = {" + ", ".join(map(str, filler)) + "};\n"
    s += varname +\
         " = Recipe(" + str(id) + ", " + str(recipe.start_module) + ", n_works" + str(id) + ", num_parents" + str(id) + ", num_children" + str(id) \
         + ", n_children_len" + str(id) + ", " + size + ", " + str(recipe.start_direction) + ");\n\n"

    return varname, s


def generate_module_declaration(module, number_of_worktypes, number_of_outputs):
    s = "// Module " + str(module.m_id) + "\n"
    wa, temp = work_array(module, number_of_worktypes)
    s += temp
    pa, temp = p_time_array(module, number_of_worktypes)
    s += temp
    na, temp = next_array(module, number_of_outputs)
    s += temp
    ta, temp = t_time_array(module, number_of_outputs)
    s += temp

    mq = STR_MODULE_QUEUE + str(module.m_id)
    s += mq + " = ModuleQueue(" + str(module.m_id) + ", " + str(module.queue_length)
    s += ", " + wa + ");\n"

    mw = STR_MODULE_WORKER + str(module.m_id)
    s += mw + " = ModuleWorker(" + str(module.m_id) + ", " + wa + ", " + pa + ");\n"

    mt = STR_MODULE_TRANSPORTER + str(module.m_id)
    s += mt + " = ModuleTransporter(" + str(module.m_id) + ", " + ta + ", " + na
    s += ", " + str(module.allow_passthrough).lower() + ");\n\n"

    return mq, mw, mt, s


def work_array(module, number_of_worktypes):
    """
    :param module:  Module for which we create a work array
    :param number_of_worktypes: Amount of unique work types total
    :return: The name of the var and a string of code that declares the var
    """
    varname = STR_WA + str(module.m_id)
    s = "const int " + varname + "[" + STR_NUMBER_OF_WORKTYPES + "] = {"
    for w_type in range(number_of_worktypes):
        if w_type in module.w_type:
            s += "true"
        else:
            s += "false"
        if w_type != number_of_worktypes - 1:
            s += ", "
    s += "};\n"

    return varname, s


def p_time_array(module, number_of_worktypes):
    varname = STR_PA + str(module.m_id)
    s = "const int " + varname + "[" + STR_NUMBER_OF_WORKTYPES + "] = {"
    for w_type in range(number_of_worktypes):
        if w_type in module.w_type:
            s += str(module.p_time[w_type])
        else:
            s += "0"
        if w_type != number_of_worktypes - 1:
            s += ", "
    s += "};\n"
    return varname, s


def next_array(module, number_of_outputs):
    varname = STR_NA + str(module.m_id)
    s = "const mid_t " + varname + "[" + STR_NUMBER_OF_OUTPUTS + "] = {"
    for i in range(number_of_outputs):
        if module.connections[i]:
            s += str(module.connections[i].m_id)
        else:
            s += "-1"
        if i != number_of_outputs - 1:
            s += ", "
    s += "};\n"
    return varname, s


def t_time_array(module, number_of_outputs):
    varname = STR_TA + str(module.m_id)
    s = "const int " + varname + "[" + STR_NUMBER_OF_OUTPUTS + "][" + STR_NUMBER_OF_OUTPUTS + "] = {"
    for i in range(number_of_outputs):
        s += "{"
        for j in range(number_of_outputs):
            s += str(module.t_time[i][j])
            if j != number_of_outputs - 1:
                s += ", "
        s += "}"
        if i != number_of_outputs - 1:
            s += ", "
    s += "};\n"
    return varname, s


def generate_system_declaration(system_list):
    """
    To system declaration, generates a string including all modules and recipes
    :param number_of_modules: total number of FESTO modules
    :param number_of_recipes: total number of recipes
    :return: string to add all recipes and modules to system
    """
    s = "system "
    for i, item in enumerate(system_list):
        s += item
        if i != len(system_list) - 1:
            s += ", "

    s += ";"
    return s


def create_query(recipe_names, new_file_name="test.q"):
    """
    Generates a query file, containing a query to check whether all recipes are done.
    :param recipe_names: Names of the recipes for which a query will be generated
    :param new_file_name: path to new file
    """
    s = "E<> "
    for i, recipe in enumerate(recipe_names):
        s += recipe + ".done"
        if i != len(recipe_names) - 1:
            s += " and "
    f = open(new_file_name, 'w')
    f.write(s)
    f.close()


m0 = SquareModule(0, [0, 1, 2], {0: 2, 1: 2, 2: 3}, {0: 0, 1: 2, 2: 0}, [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]], 3, True)
m0.up = m0

t0 = [[-1, -1, -1, -1],
      [-1, -1, -1, 117],
      [-1, -1, -1, -1],
      [-1, 117, -1, -1]]
m0 = SquareModule(0, [0], {0: 60}, {0: 1}, t0, 3)

t1 = [[-1, -1, -1, -1],
      [-1, -1, -1, 107],
      [-1, -1, -1, -1],
      [-1, 107, -1, -1]]

m1 = SquareModule(1, [1, 2], {1: 53, 2: 106}, {1: 1, 2: 1}, t1, 3)


t2 = [[-1, -1, -1, -1],
      [-1, -1, -1, 164],
      [-1, -1, -1, -1],
      [-1, 164, -1, -1]]

m2 = SquareModule(2, [3, 4, 5], {3: 582, 4: 752, 5: 850}, {3: 1, 4: 1, 5: 1}, t2, 3, allow_passthrough=True)

t3 = [[-1, -1, -1, -1],
      [-1, -1, -1, 112],
      [-1, -1, -1, -1],
      [-1, 112, -1, -1]]

m3 = SquareModule(3, [6], {6: 20}, {6: 1}, t3, 3)

t4 = [[-1, -1, -1, -1],
      [-1, -1, -1, 112],
      [-1, -1, -1, -1],
      [-1, 112, -1, -1]]

m4 = SquareModule(4, [], {}, {}, t4, 3, allow_passthrough=True)

t5 = [[-1, -1, -1, -1],
      [-1, -1, -1, -1],
      [-1, -1, -1, -1],
      [-1, 0, -1, -1]]

m5 = SquareModule(5, [7], {7: 68}, {7: 1}, t5, 3, allow_passthrough=True)


m0.right = m1
m1.right = m2
m2.right = m3
m3.right = m4
m4.right = m5

modules = [m0, m1, m2, m3, m4, m5]

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
generate_xml("../../Modeler/iter3.2.xml", modules, [r0, r1, r2])