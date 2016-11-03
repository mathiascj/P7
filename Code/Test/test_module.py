from copy import deepcopy
from unittest import TestCase
from hypothesis import given

from Test.strategies import modules
from module import Module


class TestModule(TestCase):

  @given(modules())
  def test_module_equality(self, mod1, mod2):
    mod1_cpy = deepcopy(mod1)
    mod2_cpy = deepcopy(mod2)
    assert mod1 == mod1_cpy
    assert mod2 == mod2_cpy
    if mod1.module_id == mod2.module_id and \
       mod1.connections == mod2.connections and \
       mod1.work_type == mod2.worktype and \
       mod1.cost_rate == mod2.cost_rate and \
       mod1.processing_time == mod2.processing_time and \
       mod1.transport_time == mod2.transport_time:
      assert mod1 == mod2
    else:
      assert not mod1 == mod2

  @given(modules())
  def test_get_connections_correct_length(self, mod):
    assert len(mod.get_connections()) == len(mod.connections)

  @given(modules())
  def test_get_connections_correct_type(self, mod):
    assert isinstance(mod.get_connections(), list)
    for elem in mod.get_connections():
      assert isinstance(elem, int)

  @given(modules())
  def test_module_equality(self, mod):
    mod2 = Module(mod.module_id, mod.work_type, mod.processing_time, mod.transport_time, mod.cost_rate, mod.connections)
    assert mod == mod2
    assert not mod != mod2
