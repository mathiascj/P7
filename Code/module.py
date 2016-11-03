class Module:
  """
  Represents a module in the Festo system
  """

  def __init__(self, module_id, work_type, processing_time, transport_time, cost_rate, connections):
    """
    :param module_id: A unique identifier for the module
    :param connections: A list of IDs, which the module connects to.
    :param work_type: An identifier for the work type of the module (integer)
    :param processing_time: An integer specifying the processing time of the module
    :param transport_time: An integer specifying the transport time of the module
    """

    if module_id == 0:
      raise ValueError("Module_id may not be set to 0")
    else:
      self.module_id = module_id
    self.connections = connections
    self.work_type = work_type
    self.cost_rate = cost_rate
    self.processing_time = processing_time
    self.transport_time = transport_time

  def __eq__(self, other):
      if isinstance(other, self.__class__):
        return self.__dict__ == other.__dict__
      else:
          return False

  def __ne__(self, other):
      return not self.__eq__(other)

  def __hash__(self):
    return hash(tuple(sorted(self.__dict__)))

  def __str__(self):
    s = ""
    s += "{module_id: " + str(self.module_id) + ", "
    s += "connections: ["
    for con in self.connections:
      s += str(con.module_id) + ", "
    if len(self.connections) != 0:
      s = s[:-2]
    return s + "]}"

  def __repr__(self):
    return str(self)

  def get_connections(self):
    """
    :return: A list of IDs, which the module connects to
    """
    res = []
    for i in range(0, len(self.connections)):
      res.append(self.connections[i].module_id)
    return res


def printable_paths(paths):
  """
  Used for debugging purposes.
  :param paths: a list of paths, i.e. a list of list of modules
  :return: paths as a string in a printable format
  """
  s = "["
  for path in paths:
    s += printable_path(path) + ", "
  if len(s) > 1:
    return s[:-2] + "]"
  else:
    return s + "]"


def printable_path(path):
  """
  Used for debugging purposes.
  :param path: a single path, i.e a list of modules
  :return: a path as a string in a printable format
  """
  s = "["
  for module in path:
    if type(module) is Module:
      s += str(module.module_id) + ", "
    else:
      s += "(Looping index: " + str(module) + ") "
  if len(s) > 1:
    return s[:-2] + "]"
  else:
    return s + "]"
