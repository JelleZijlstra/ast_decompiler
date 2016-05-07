**************
ast_decompiler
**************

ast_decompiler is a module for generating Python code given an AST.

A usage example::

    >> import ast
    >> from ast_decompiler import decompile

    >> decompile(ast.parse('(a + b) * c'))
    (a + b) * c

This module has only been tested on Python 2.7.
