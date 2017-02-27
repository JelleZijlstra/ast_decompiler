from .tests import assert_decompiles


def test_module_docstring():
    assert_decompiles('''
"""
module docstring
"""


class A():
    """
    class docstring
    """
    def b():
        """
        function docstring
        """
''', '''
"""
module docstring
"""


class A():
 """
 class docstring
 """
 def b():
  """
  function docstring
  """
''', indentation=1)
