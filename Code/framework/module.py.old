def ve_msg(m1, m2):
    return 'Can not connect ' + str(m1.__class__) + " to " + str(m2.__class__)

def re_msg(m, attr):
    return 'The attribute ' + attr + ' is not available in ' + str(m.__class__)


class FestoModule:
    """ Representation of a Festo Module. Contains commonly used information such as work type, processing time, travel
    time, cost rate and id. Also contains other festo modules, in the right, up, down, attributes, which represents the
    modules it can connect to.
    """
    # TODO: Make set down functionality
    def __init__(self, out_right, out_up, out_down, id, w_type, p_time, t_time, c_rate):
        """
        :param right: A FestoModule, must have a left input, i.e. right.in_avail_dict['L'] == True
        :param up:  A FestoModule, must have an up input
        :param down: A FestoModule, must have a down input
        :param id: An unique ID for the module. WARNING: It being unique is not enforced
        :param w_type: An ID specifying what kind of work this module can produce.
        :param p_time: An integer representing the amount of time it takes to process the above mentioned work
        :param t_time: An integer representing the amount of time it takes to travel through the module
        :param c_rate: An integer representing the cost of processing in this module
        """
        # private members:
        self._out_right = None
        self._out_up = None
        self._out_down = None
        self._in_left = None
        self._in_up = None
        self._in_down = None

        # Properties
        self.out_right = out_right
        self.out_up = out_up
        self.out_down = out_down

        # Regular Attributes
        self.id = id
        self.w_type = w_type
        self.p_time = p_time
        self.t_time = t_time
        self.c_rate = c_rate

        self.in_avail_dict = {'L': False, 'U': False, 'D': False}

    def get_conn_out(self):
        return {'R': self._right, 'U': self._up, 'D': self._down}

    def set_conn_out(self, conn_out_dict):
        self._right = conn_out_dict['R']
        self._up = conn_out_dict['U']
        self._down = conn_out_dict['D']

    @staticmethod
    def check_if_can_connect(module, direction):
        if not module:
            return True
        else:
            return module.in_avail_dict[direction]

    # right Property
    @property
    def out_right(self):
        return self._out_right

    @out_right.setter
    def out_right(self, out_right):
        if self.check_if_can_connect(out_right, 'L'):
            if self._out_right:
                self._out_right._in_left = None     # Remove ourselves from currently connected to
            if out_right:
                out_right._in_left = self           # Connect ourselves to new one
            self._out_right = out_right
        else:
            raise ValueError(ve_msg(self, out_right))

    def set_right_to_down(self, out_right):
        """ out_right setter that sets it to in_down on a module instead
        """
        if self.check_if_can_connect(out_right, 'D'):
            if self._out_right:
                self._out_right._in_down = None     # Remove ourselves from currently connected to
            if out_right:
                out_right._in_down = self           # Connect ourselves to new one
            self._out_right = out_right

        else:
            raise ValueError(ve_msg(self, out_right))

    @property
    def out_up(self):
        return self._out_up

    @out_up.setter
    def out_up(self, out_up):
        if self.check_if_can_connect(out_up, 'U'):
            if self._out_up:
                self._out_up._in_up = None      # Remove ourselves from currently connected to
            if out_up:
                out_up._in_up = self            # Connect ourselves to new one
            self._out_up = out_up

        else:
            raise ValueError(ve_msg(self, out_up))

    # down Property
    @property
    def out_down(self):
        return self._out_down

    @out_down.setter
    def out_down(self, out_down):
        if self.check_if_can_connect(out_down, 'L'):
            if self._out_down:
                self._out_down._in_left = None   # Remove ourselves from currently connected to
            if out_down:
                out_down._in_left = self    # Connect ourselves to new one
            self._out_down = out_down
        else:
            raise ValueError(ve_msg(self, out_down))

    def __repr__(self):
        s = str(self.__class__)
        s += '\n    id: ' + str(self.id)
        s += '\n    outputs:'
        if self.out_right:
            s += '\n        right -> ' + str(self.out_right.id)
        if self.out_up:
            s += '\n        up    -> ' + str(self.out_up.id)
        if self.out_down:
            s += '\n        down  -> ' + str(self.out_down.id)
        s += '\n    inputs:'
        if self._in_left:
            s += '\n        ' + str(self._in_left.id) + ' -> left'
        if self._in_up:
            s += '\n        ' + str(self._in_up.id) + ' -> up'
        if self._in_down:
            s += '\n        ' + str(self._in_down.id) + ' -> down'
        return s

    @staticmethod
    def __get_module_id(module):
        if module:
            return module.id
        else:
            return None


class WorkModule(FestoModule):
    """
    """
    def __init__(self, right, up, id, w_type, p_time, t_time, c_rate):
        super().__init__(right, up, None, id, w_type, p_time, t_time, c_rate)

    @FestoModule.out_down.getter
    def out_down(self):
        return None

    @FestoModule.out_down.setter
    def down(self, down):
        if down:
            raise RuntimeError(re_msg(self, 'down'))


class SplitterModule(FestoModule):
    """
    """
    def __init__(self, right, up, down, id, w_type, p_time, t_time, c_rate):
        super().__init__(right, up, down, id, w_type, p_time, t_time, c_rate)


class A0Module(WorkModule):
    """
    """
    def __init__(self, right, id, w_type, p_time, t_time, c_rate):
        super().__init__(right, None, id, w_type, p_time, t_time, c_rate)
        self.in_avail_dict = {'L': True, 'U': False, 'D': False}

    @FestoModule.out_up.getter
    def out_up(self):
        return None

    @FestoModule.out_up.setter
    def out_up(self, up):
        if up:
            raise RuntimeError(re_msg(self, 'up'))


class A1Module(WorkModule):
    """
    """
    def __init__(self, up, id, w_type, p_time, t_time, c_rate):
        super().__init__(None, up, id, w_type, p_time, t_time, c_rate)
        self.in_avail_dict = {'L': True, 'U': False, 'D': False}

    @FestoModule.out_right.getter
    def out_right(self):
        return None

    @FestoModule.out_right.setter
    def out_right(self, right):
        if right:
            raise RuntimeError(re_msg(self, 'right'))


class A2Module(WorkModule):
    """
    """
    def __init__(self, right, id, w_type, p_time, t_time, c_rate):
        super().__init__(right, None, id, w_type, p_time, t_time, c_rate)
        self.in_avail_dict = {'L': False, 'U': True, 'D': False}

    @FestoModule.out_up.getter
    def out_up(self):
        return None

    @FestoModule.out_up.setter
    def out_up(self, up):
        if up:
            raise RuntimeError(re_msg(self, 'up'))


class A3Module(WorkModule):
    """
    """
    def __init__(self, up, id, w_type, p_time, t_time, c_rate):
        super().__init__(None, up, id, w_type, p_time, t_time, c_rate)
        self.in_avail_dict = {'L': False, 'U': True, 'D': False}

    @FestoModule.out_right.getter
    def out_right(self):
        return None

    @FestoModule.out_right.setter
    def out_right(self, right):
        if right:
            raise RuntimeError(re_msg(self, 'right'))


class A4Module(WorkModule):
    """
    """
    def __init__(self, right, id, w_type, p_time, t_time, c_rate):
        super().__init__(right, None, id, w_type, p_time, t_time, c_rate)
        self.in_avail_dict = {'L': True, 'U': True, 'D': False}

    @FestoModule.out_up.getter
    def out_up(self):
        return None

    @FestoModule.out_up.setter
    def out_up(self, up):
        if up:
            raise RuntimeError(re_msg(self, 'up'))


class A5Module(WorkModule):
    """
    """
    def __init__(self, up, id, w_type, p_time, t_time, c_rate):
        super().__init__(None, up, id, w_type, p_time, t_time, c_rate)
        self.in_avail_dict = {'L': True, 'U': True, 'D': False}

    @FestoModule.out_right.getter
    def out_right(self):
        return None

    @FestoModule.out_right.setter
    def out_right(self, right):
        if right:
            raise RuntimeError(re_msg(self, 'right'))


class U0I0Module(SplitterModule):
    """
    """
    def __init__(self, right, down, id, w_type, p_time, t_time, c_rate):
        super().__init__(right, None, down, id, w_type, p_time, t_time, c_rate)
        self.in_avail_dict = {'L': True, 'U': False, 'D': True}

    @FestoModule.out_up.getter
    def out_up(self):
        return None

    @FestoModule.out_up.setter
    def out_up(self, up):
        if up:
            raise RuntimeError(re_msg(self, 'up'))


class U0I1Module(SplitterModule):
    """
    """
    def __init__(self, up, down, id, w_type, p_time, t_time, c_rate):
        super().__init__(None, up, down, id, w_type, p_time, t_time, c_rate)
        self.in_avail_dict = {'L': True, 'U': False, 'D': True}

    @FestoModule.out_right.getter
    def out_right(self):
        return None

    @FestoModule.out_right.setter
    def out_right(self, right):
        if right:
            raise RuntimeError(re_msg(self, 'right'))


class U1I0Module(SplitterModule):
    """
    """
    def __init__(self, right, down, id, w_type, p_time, t_time, c_rate):
        super().__init__(right, None, down, id, w_type, p_time, t_time, c_rate)
        self.in_avail_dict = {'L': False, 'U': True, 'D': True}

    @FestoModule.out_up.getter
    def out_up(self):
        return None

    @FestoModule.out_up.setter
    def out_up(self, up):
        if up:
            raise RuntimeError(re_msg(self, 'up'))


class U1I1Module(SplitterModule):
    """
    """
    def __init__(self, up, down, id, w_type, p_time, t_time, c_rate):
        super().__init__(None, up, down, id, w_type, p_time, t_time, c_rate)
        self.in_avail_dict = {'L': False, 'U': True, 'D': True}

    @FestoModule.out_right.getter
    def out_right(self):
        return None

    @FestoModule.out_right.setter
    def out_right(self, right):
        if right:
            raise RuntimeError(re_msg(self, 'right'))


class U2I0Module(SplitterModule):
    """
    """
    def __init__(self, right, down, id, w_type, p_time, t_time, c_rate):
        super().__init__(right, None, down, id, w_type, p_time, t_time, c_rate)
        self.in_avail_dict = {'L': True, 'U': True, 'D': True}

    @FestoModule.out_up.getter
    def out_up(self):
        return None

    @FestoModule.out_up.setter
    def out_up(self, up):
        if up:
            raise RuntimeError(re_msg(self, 'up'))


class U2I1Module(SplitterModule):
    """
    """
    def __init__(self, up, down, id, w_type, p_time, t_time, c_rate):
        super().__init__(None, up, down, id, w_type, p_time, t_time, c_rate)
        self.in_avail_dict = {'L': True, 'U': True, 'D': True}

    @FestoModule.out_right.getter
    def out_right(self):
        return None

    @FestoModule.out_right.setter
    def out_right(self, right):
        if right:
            raise RuntimeError(re_msg(self, 'right'))



