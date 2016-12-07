import re

class ConfigStringHandler:
    def __init__(self, recipes, all_modules, initial_configuration=""):
        self.all_modules = all_modules
        self.recipes = recipes

        self.free_modules = all_modules
        self.current_modules = []

        self.module_dictionary = {m.m_id: m for m in all_modules}
        self.recipe_dictionary = {r.name: r for r in recipes}

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
        for m in self.all_modules:
            m.up = None
            m.right = None
            m.down = None
            m.left = None
            m.active_w_type = set()

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
