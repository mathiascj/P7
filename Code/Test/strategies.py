from hypothesis import assume, strategies as st
from module import Module
import random
from copy import deepcopy


@st.composite
def modules(draw):
  m_id = draw(st.integers(min_value=1))
  w_id = draw(st.integers())
  p_time = draw(st.integers())
  t_time = draw(st.integers())
  c_rate = draw(st.integers(min_value=0))
  cons = []
  return Module(m_id, w_id, p_time, t_time, c_rate, cons)


@st.composite
def configurations(draw, min_num_of_modules=0):
  mods = draw(st.lists(modules()))
  assume(len(mods) >= min_num_of_modules)
  return mods


@st.composite
def proper_configurations(draw):
  num_of_modules = random.randint(2, 10)
  mods = []
  for i in range(1, num_of_modules + 1):
    m_id = i
    w_type = draw(st.integers())
    p_time = draw(st.integers())
    t_time = draw(st.integers())
    c_rate = draw(st.integers())
    # cons = draw(st.lists(st.integers(min_value=i, max_value=num_of_modules).filter(lambda x: x != i), max_size=4, unique=True))
    mods.append(Module(m_id, w_type, p_time, t_time, c_rate, []))

  modules_without_connections = deepcopy(mods)
  current_module = random.choice(modules_without_connections)
  modules_without_connections.remove(current_module)

  while len(modules_without_connections) > 0:
    if len(current_module.connections) < 4:
      random_choice = random.choice(modules_without_connections)
      current_module.connections.append(random_choice)
      mods[mods.index(next(mod for mod in mods if mod.module_id == current_module.module_id))] = current_module
      modules_without_connections.remove(random_choice)
    if len(current_module.connections) == 4:
      current_module = random.choice(current_module.connections)
  return mods

