from unittest import TestCase
from hypothesis import given

from module import Module
from Validation.configuration_validation import contains_only_one_line, get_paths, is_valid
from Test.strategies import configurations, proper_configurations


class TestConfiguration(TestCase):

  @given(configurations())
  def test_contains_only_one_line_correct_type(self, mods):
    assert isinstance(contains_only_one_line(mods), bool)

  @given(configurations())
  def test_contains_only_one_line_always_same_answer(self, mods):
    assert contains_only_one_line(mods) == contains_only_one_line(mods)

  @given(proper_configurations())
  def test_proper_configurations_always_create_connected_configurations(self, mods):
    assert contains_only_one_line(mods)

  @given(proper_configurations())
  def test_get_paths_correct_type(self, mods):
    paths = get_paths(mods, mods[0], [[mods[0]]])
    assert isinstance(paths, list)
    for path in paths:
      assert isinstance(path, list)
      assert isinstance(path[0], int) or isinstance(path[0], Module)
      for module in path[1:]:
        assert isinstance(module, Module)

  def test_create_dependencies(self):
    pass

  def test_is_placeable(self):
    pass

  @given(proper_configurations())
  def test_is_valid(self, modules):
    if is_valid(modules):
      for module in modules:
        assert len(module.get_connections()) <= 4  # no more than 4 connections
        assert module.module_id not in module.get_connections()  # cannot connect to itself
        for connection in module.get_connections():
          assert any(x.module_id == connection for x in modules)
