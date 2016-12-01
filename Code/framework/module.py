import re

class Module:
    """ Module class that contains all the required information for XML to be generated to the UPPAAL model. Represents
    a real life factory module, in that it is identifiable with m_id, does some work w_type, that takes p_time.
    Furthermore it takes t_time to travel through the module.
    """
    def __init__(self, connections, m_id, w_type, p_time, t_time):
        self.connections = connections
        self.m_id = m_id
        self.w_type = w_type
        self.p_time = p_time
        self.t_time = t_time


class SquareModule(Module):
    """ Represents Square Modules, where each edge can connect and be connected to be adjacent modules. This results in
    a grid like pattern for the entire factory configuration.
    """
    def __init__(self, m_id, w_type, p_time,  t_time, queue_length, allow_passthrough=False, up=None, down=None,
                 left=None, right=None):
        """
        :param m_id: Id of the module, has to be unique for each module
        :param w_type: A list of work types that this module is capable of performing, worktypes should be unique
        integers
        :param p_time: A dict of processing times, key is w_type and value the processing time
        :param t_time: A 4x4 array (list) that defines the travel time from each input to each output of the module
        :param queue_length: An integer specifying how many recipes that can be in the queue on the module
        :param allow_passthrough: Boolean that specifies wether a recipe can skip working on a module and just go
        straight to transporting
        :param up: ID of the module situated above
        :param down: ID of the module situated below
        :param left: ID of the module situated to the left
        :param right: ID of the module situated to the rigth
        """
        # Private members, instantiated here for the sake of readability
        self.__up = None
        self.__down = None
        self.__left = None
        self.__right = None

        self.__in_up = None
        self.__in_down = None
        self.__in_left = None
        self.__in_right = None

        self.__connections = [self.up, self.right, self.down, self.left]

        # Attributes
        self.queue_length = queue_length
        self.allow_passthrough = allow_passthrough

        # Properties
        self.up = up
        self.down = down
        self.left = left
        self.right = right

        self.active_w_type = set()


        # Checks
        if str(m_id) in self.modules_dictionary:
            raise KeyError('m_id is not unique, a ' + str(self.modules_dictionary[str(m_id)]) + ' already exists')
        else:
            self.modules_dictionary[str(m_id)] = self

        if len(t_time) != 4:
            raise ValueError("t_time needs to be a 4x4 array")

        for i in range(4):
            if len(t_time[i]) != 4:
                raise ValueError("t_time needs to be a 4x4 array")

        if len(w_type) != len(p_time):
            raise ValueError("w_type and p_time should be of equal length. Recieved lengths w_type: " + str(len(w_type))
                             + " and p_time: " + str(len(p_time)))

        super().__init__(connections=[up, right, down, left],
                         m_id=m_id,
                         w_type=w_type,
                         p_time=p_time,
                         t_time=t_time)

    # STATIC VARS
    modules_dictionary = {}

    @property
    def connections(self):
        return [self.up, self.right, self.down, self.left]

    @connections.setter
    def connections(self, connections):
        if len(connections) == 4:
            self.__connections = list(connections)
        else:
            raise ValueError("Connections must be an iterable of size 4")


    @property
    def __in_connections(self):
        return [self.__in_up, self.__in_right, self.__in_down, self.__in_left]

    @property
    def up(self):
        return self.__up

    @up.setter
    def up(self, up):
        if self.__up:                   # Remove ourselves from currently connected to
            self.__up.__in_down = None
        if up:                          # Add ourselves to new
            up.__in_down = self
        self.__up = up

    @property
    def down(self):
        return self.__down

    @down.setter
    def down(self, down):
        if self.__down:
            self.__down.__in_up = None
        if down:
            down.__in_up = self
        self.__down = down

    @property
    def left(self):
        return self.__left

    @left.setter
    def left(self, left):
        if self.__left:
            self.__left.__in_right = None
        if left:
            left.__in_right = self
        self.__left = left

    @property
    def right(self):
        return self.__right

    @right.setter
    def right(self, right):
        if self.__right:
            self.__right.__in_left = None
        if right:
            right.__in_left = self
        self.__right = right

    def make_grid(self, pos=(0, 0), ignore={None}):
        """ Makes a grid with the current module as its center, i.e. coordinates (0, 0)
        :param pos: Position that a module is relative to module who started the call. The module that starts the call
        shouldn't use this parameter. Defaults to (0, 0) as the module that starts the call should be in the center of
        the grid.
        :param ignore: A set of modules that are ignore, is used to so that we don not cycle.
        :return: A dictionary, were the keys are modules and the values are a tuple representing their position in the
        grid.
        """
        # We add ourselves to the grid at position pos
        grid = {self: pos}

        # The ignore set is copied, because ignore is mutable and it would therefor fuck up subsequent calls if we used
        # it directly
        ignore_c = ignore.copy()

        # We add ourselves to the ignore set, so that we wont be called again in the future.
        ignore_c.add(self)

        # We add our up, down, right, left to the grid
        if self.up not in ignore_c:
            grid.update(self.up.make_grid((pos[0], pos[1] + 1), ignore_c))
        if self.down not in ignore_c:
            grid.update(self.down.make_grid((pos[0], pos[1] - 1), ignore_c))
        if self.right not in ignore_c:
            grid.update(self.right.make_grid((pos[0] + 1, pos[1]), ignore_c))
        if self.left not in ignore_c:
            grid.update(self.left.make_grid((pos[0] - 1, pos[1]), ignore_c))

        # We add __in_up, __in_down, __in_right, __in_left to the grid. This is done to make sure we catch all modules
        # and not only the ones are successors to this module.
        if self.__in_up not in ignore_c:
            grid.update(self.__in_up.make_grid((pos[0], pos[1] + 1), ignore_c))
        if self.__in_down not in ignore_c:
            grid.update(self.__in_down.make_grid((pos[0], pos[1] - 1), ignore_c))
        if self.__in_right not in ignore_c:
            grid.update(self.__in_right.make_grid((pos[0] + 1, pos[1]), ignore_c))
        if self.__in_left not in ignore_c:
            grid.update(self.__in_left.make_grid((pos[0] - 1, pos[1]), ignore_c))

        return grid

    def can_connect(self, module, direction):
        """ Checks whether or not a module can be connect to this one in a good ol' practical way.
        :param module: The module you wish to connect
        :param direction: The direction in which you wish to connect it
        :return: A boolean, stating whether or not the module could be practically connected
        """
        grid = self.make_grid()
        if module in grid.keys():
            return grid[module] == direction
        elif module not in grid.keys():
            return direction not in grid.values()

    def swap(self, module):
        module.up = self.up
        self.__up = None
        module.right = self.right
        self.__right = None
        module.down = self.down
        self.__down = None
        module.left = self.left
        self.__left = None
        self.active_w_type = set()

    def find_connected_modules(self, ignore={None}):
        ignore_c = ignore.copy()
        ignore_c.add(self)
        L = [self]
        for m in self.connections:
            if m not in ignore_c:
                L += m.find_connected_modules(ignore_c)
        for m in self.__in_connections:
            if m not in ignore_c:
                L += m.find_connected_modules(ignore_c)
        return L

    @staticmethod
    def configuration_str(module):
        configuration = module.find_connected_modules()
        configuration.sort(key=lambda m: m.m_id)        # Sorts the list based on m_id

        L = []
        for m in configuration:
            s = str(m.m_id) + '{' + ','.join(map(str, m.active_w_type)) + '}'
            s += '[' + ','.join(map(str, map(lambda x: x.m_id if x else '_', m.connections))) + ']'
            L.append(s)

        return ':'.join(L)

    @staticmethod
    def make_configuration(configuration_str):
        if not isinstance(configuration_str, str):
            raise ValueError("configuration_str should be a string!")
        for m in SquareModule.modules_dictionary.values():
            m.up = None
            m.right = None
            m.down = None
            m.left = None
            m.active_w_type = set()

        L = configuration_str.split(sep=':')
        for ms in L:
            m_id = re.search('(.*)(?=\{)', ms).group(0) # (?=...) is a lookahead assertion
            active_w_type = set(re.search('.*\{(.*)\}.*', ms).group(1).split(sep=','))
            temp = re.search('.*\[(.*)\].*', ms).group(1).split(sep=',')
            connections = [SquareModule.modules_dictionary[conn_id] if conn_id != '_' else None for conn_id in temp]

            SquareModule.modules_dictionary[m_id].active_w_type = active_w_type
            SquareModule.modules_dictionary[m_id].up = connections[0]
            SquareModule.modules_dictionary[m_id].right = connections[1]
            SquareModule.modules_dictionary[m_id].down = connections[2]
            SquareModule.modules_dictionary[m_id].left = connections[3]


    def pprint(self):
        """ Pretty Prints a module
        """
        s = str(self.__class__)
        s += "\n    Self  == " + str(self.m_id)
        s += "\n    Up    -> " + str((lambda m: m.m_id if m else '_')(self.up))
        s += "\n    Down  -> " + str((lambda m: m.m_id if m else '_')(self.down))
        s += "\n    Left  -> " + str((lambda m: m.m_id if m else '_')(self.left))
        s += "\n    Right -> " + str((lambda m: m.m_id if m else '_')(self.right))
        print(s)

    def __repr__(self):
        return "module_" + str(self.m_id)




