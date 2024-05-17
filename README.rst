**************
ast_decompiler
**************

ast_decompiler is a module for generating Python code given an AST.

A usage example::

    >> import ast
    >> from ast_decompiler import decompile

    >> decompile(ast.parse('(a + b) * c'))
    (a + b) * c

This module supports Python 3.8 through 3.13.

====================
Tests and formatting
====================

To run the tests, install ``pytest`` in a virtual environment. Then, either use
``tox``, or simply run ``pytest tests/``.

The code is formatted with Black.
