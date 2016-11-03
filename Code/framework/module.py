class Module:
    """ Module class that contains all the required information for XML to be generated to the UPPAAL model. Represents
    a real life factory module, in that it is identifiable with m_id, does some work w_type, that takes p_time and costs
    c_rate pre time. Furthermore it takes t_time to travel through the module.
    """
    def __init__(self, connections, m_id, w_type, p_time, t_time, c_rate):
        self.connections = connections
        self.m_id = m_id
        self.w_type = w_type
        self.p_time = p_time
        self.t_time = t_time
        self.c_rate = c_rate


def get_id(module):
    if module:
        return module.m_id
    else:
        return None


class SquareModule(Module):
    """ Represents Square Modules, where each edge can connect and be connected to be adjacent modules. This results in
    a grid like pattern for the entire factory configuration.
    """
    def __init__(self, m_id, w_type, p_time, t_time, c_rate, up=None, down=None, left=None, right=None):
        # Private members, instantiated here for the sake of readability
        self.__up = None
        self.__down = None
        self.__left = None
        self.__right = None

        # Properties
        self.up = up
        self.down = down
        self.left = left
        self.right = right

        super().__init__(connections=[up, down, left, right],
                         m_id=m_id,
                         w_type=w_type,
                         p_time=p_time,
                         t_time=t_time,
                         c_rate=c_rate)

    @property
    def up(self):
        return self.__up

    @up.setter
    def up(self, up):
        if self.__up:                   # Remove ourselves from currently connected to
            self.__up.__down = None
        if up:                          # Add ourselves to new
            up.__down = self
        self.__up = up

    @property
    def down(self):
        return self.__down

    @down.setter
    def down(self, down):
        if self.__down:
            self.__down.__up = None
        if down:
            down.__up = self
        self.__down = down

    @property
    def left(self):
        return self.__left

    @left.setter
    def left(self, left):
        if self.__left:
            self.__left.__right = None
        if left:
            left.__right = self
        self.__left = left

    @property
    def right(self):
        return self.__right

    @right.setter
    def right(self, right):
        if self.__right:
            self.__right.__left = None
        if right:
            right.__left = self
        self.__right = right

    def make_grid(self, start_pos=(0, 0), ignore={None}):
        grid = {start_pos: self.m_id}
        ignore.add(self)
        if self.up not in ignore:
            grid.update(self.up.make_grid((start_pos[0], start_pos[1] + 1), ignore))
        if self.down not in ignore:
            grid.update(self.down.make_grid((start_pos[0], start_pos[1] - 1), ignore))
        if self.left not in ignore:
            grid.update(self.left.make_grid((start_pos[0] - 1, start_pos[1]), ignore))
        if self.right not in ignore:
            grid.update(self.right.make_grid((start_pos[0] + 1, start_pos[1]), ignore))
        return grid

    def __repr__(self):
        s = str(self.__class__)
        s += "\n    Up    -> " + str(get_id(self.up))
        s += "\n    Down  -> " + str(get_id(self.down))
        s += "\n    Left  -> " + str(get_id(self.left))
        s += "\n    Right -> " + str(get_id(self.right))
        return s





