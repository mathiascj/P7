import re
from copy import deepcopy

class ConfigStringHandler:
    def __init__(self, recipes, all_modules, transport_module, initial_configuration=""):
        self.all_modules = all_modules
        self.recipes = recipes
        self.transport_module = transport_module

        self.free_modules = all_modules

        self.current_modules = []

        self.free_transporters = []

        self.module_dictionary = {m.m_id: m for m in all_modules}
        self.recipe_dictionary = {r.name: r for r in recipes}

        self.transport_id = 0

        if initial_configuration:
            self.make_configuration(initial_configuration)

    def configuration_str(self):
        if self.current_modules:
            configuration = self.current_modules[0].find_connected_modules()
            configuration.sort(key=lambda m: m.m_id)        # Sorts the list based on m_id

            R = [r.recipe_str() for r in self.recipes]
            M = [m.module_str() for m in configuration]

            return "$".join(R) + "|" + ':'.join(M)
        else:
            return ""

    def make_configuration(self, configuration_str):
        if not isinstance(configuration_str, str):
            raise ValueError("configuration_str should be a string!")
        self.current_modules = []
        self.reset_modules()

        S = configuration_str.split(sep="|")
        R = S[0].split(sep='$')
        for rs in R:
            split1 = rs.find('@')
            split2 = rs.find('&')

            name = rs[:split1]
            start_module = rs[split1 + 1:split2]
            start_direction = int(rs[split2 + 1:])

            self.recipe_dictionary[name].start_module = start_module
            self.recipe_dictionary[name].start_direction = start_direction

        M = S[1].split(sep=':')
        for ms in M:
            m_id = re.search('(.*)(?=\{)', ms).group(0)  # (?=...) is a lookahead assertion
            active_w_type = set(re.search('.*\{(.*)\}.*', ms).group(1).split(sep=','))
            temp = re.search('.*\[(.*)\].*', ms).group(1).split(sep=',')
            connections = [self.module_dictionary[conn_id] if conn_id != '_' else None for conn_id in temp]

            module = self.module_dictionary[m_id]
            module.active_w_type = active_w_type
            module.up = connections[0]
            module.right = connections[1]
            module.down = connections[2]
            module.left = connections[3]
            self.current_modules.append(module)

        self.free_modules = [m for m in self.all_modules if m not in self.current_modules]
        main_line, up_line, down_line = self.find_lines()


        for mod in self.all_modules:
            mod.shadowed = False
            mod.is_start = False
            mod.is_end = False

        up_module = None
        down_module = None
        potential_up_shadow = []
        potential_down_shadow = []

        for mod in main_line:
           if mod.up:
               up_module = mod
               potential_up_shadow = [up_module]
               mod.shadowed = True
               mod.is_start = True
           elif mod.in_up:
               up_module = None
               mod.is_end = True
               potential_up_shadow.append(mod)


               for m in potential_up_shadow:
                   m.shadowed = True
               potential_up_shadow = []

           elif up_module:
               potential_up_shadow.append(mod)

           if mod.down:
                down_module = mod
                potential_down_shadow = [down_module]
                mod.shadowed = True
                mod.is_start = True
           elif mod.in_down:
                down_module = None
                mod.is_end = True
                potential_down_shadow.append(mod)
                for m in potential_down_shadow:
                    m.shadowed = True
                potential_down_shadow = []

           elif down_module:
                potential_down_shadow.append(mod)


    def modules_in_config(self, configuration_str):
        """ Creates a list of modules that are in the configuration string.
        :param Configuration_str: A string representing a configuration, retrived by the configuration_str method
        :return: A list of modules that are in configuration_str
        """
        if not isinstance(configuration_str, str):
            raise ValueError("configuration_str should be a string!")
        result = []
        S = configuration_str.split(sep='|')
        M = S[1].split(sep=':')
        for ms in M:
            m_id = re.search('(.*)(?=\{)', ms).group(0)  #
            result.append(self.module_dictionary[m_id])

        return result

    def modules_not_in_config(self, configuration_str):
        """ The inverse of modules_in_config
        :param configuration_str: A string representing a configuration, retrived by the configuration_str method
        :return: All modules that are not in the configuration_str
        """
        in_str = self.modules_in_config(configuration_str)
        return [m for m in self.module_dictionary.values() if m not in in_str]

    def reset_modules(self):
        for m in self.all_modules:
            m.up = None
            m.right = None
            m.down = None
            m.left = None
            m.active_w_type = set()

    def make_grid(self):
        if self.current_modules:
            return self.current_modules[0].make_grid()
        else:
            return {}


    def grid_conflicts(self):

        def invert_dict(d):
            res = {}
            for k in d:
                res.setdefault(d[k], set()).add(k)
            return res

        grid = self.make_grid()
        inverted_grid = invert_dict(grid)
        conflicts = {k: v for k, v in inverted_grid.items() if len(v) > 1}
        return conflicts

    def take_transport_module(self):
        if self.free_transporters:
            t = self.free_transporters[0]
            self.free_transporters.remove(t)
        else:
            t = deepcopy(self.transport_module)
            t.m_id = "transporter" + str(self.transport_id)
            self.module_dictionary[t.m_id] = t
            self.transport_id += 1
            self.all_modules.append(t) #TODO: Adder også til current_modules. Find hvorfor.

        return  t

    def free_transport_module(self, t):
        self.current_modules.remove(t)
        t.total_wipe()
        self.free_transporters.append(t)

    def set_active_work(self, worked):
        for m, works in worked.items():
            if m in self.current_modules:
                m.active_w_type = set(works)

    def find_lines(self):
        lines = []
        for mod in self.current_modules:
            mod_in_line = False
            for l in lines:
                if mod in l:
                    mod_in_line = True

            if not mod_in_line:
                all_left = mod.traverse_in_left()
                all_left.remove(all_left[-1])
                all_right = mod.traverse_right()
                lines.append(all_left + all_right)

        # main_line = max(lines, key=len)
        main_line = lines[0]

        down_lines = []
        up_lines = []

        c_lines = lines.copy()

        # Categorize lines starting on main line
        for mod in main_line:
            if mod.up:
                for l in c_lines:
                    if l[0] == mod.up:
                        up_lines.append(l)
                        c_lines.remove(l)

            if mod.down:
                for l in c_lines:
                    if l[0] == mod.down:
                        down_lines.append(l)
                        c_lines.remove(l)

        # Categorize lines that only end on main line
        for l in c_lines:
            if l[-1].down in main_line:
                up_lines.append(l)
            elif l[-1].up in main_line:
                down_lines.append(l)

        return main_line, up_lines, down_lines

