"""

Implementation of the decompiler class.

"""
import ast
from contextlib import contextmanager

_OP_TO_STR = {
    ast.Add: '+',
    ast.Sub: '-',
    ast.Mult: '*',
    ast.Div: '/',
    ast.Mod: '%',
    ast.Pow: '**',
    ast.LShift: '<<',
    ast.RShift: '>>',
    ast.BitOr: '|',
    ast.BitXor: '^',
    ast.BitAnd: '&',
    ast.FloorDiv: '//',
    ast.Invert: '~',
    ast.Not: 'not ',
    ast.UAdd: '+',
    ast.USub: '-',
    ast.Eq: '==',
    ast.NotEq: '!=',
    ast.Lt: '<',
    ast.LtE: '<=',
    ast.Gt: '>',
    ast.GtE: '>=',
    ast.Is: 'is',
    ast.IsNot: 'is not',
    ast.In: 'in',
    ast.NotIn: 'not in',
}
_PRECEDENCE = {
    ast.Or: 0,
    ast.And: 1,
    ast.Not: 2,
    ast.Compare: 3,
    ast.BitOr: 4,
    ast.BitXor: 5,
    ast.BitAnd: 6,
    ast.LShift: 7,
    ast.RShift: 7,
    ast.Add: 8,
    ast.Sub: 8,
    ast.Mult: 9,
    ast.Div: 9,
    ast.FloorDiv: 9,
    ast.Mod: 9,
    ast.UAdd: 10,
    ast.USub: 10,
    ast.Invert: 10,
    ast.Pow: 11,
    ast.Subscript: 12,
    ast.Call: 12,
    ast.Attribute: 12,
}


def decompile(ast):
    decompiler = Decompiler()
    decompiler.visit(ast)
    return ''.join(decompiler.data)


class Decompiler(ast.NodeVisitor):
    def __init__(self):
        self.data = []
        self.indentation = 0
        self.node_stack = []

    def visit(self, node):
        self.node_stack.append(node)
        try:
            return super(Decompiler, self).visit(node)
        finally:
            self.node_stack.pop()

    def precedence_of_node(self, node):
        if isinstance(node, (ast.BinOp, ast.UnaryOp)):
            return _PRECEDENCE[type(node.op)]
        return _PRECEDENCE.get(type(node), -1)

    def write(self, code):
        assert isinstance(code, basestring), 'invalid code %r' % code
        self.data.append(code)

    def write_indentation(self):
        self.write(' ' * self.indentation)

    def write_expression_list(self, nodes, separator=', '):
        first = True
        for node in nodes:
            if first:
                first = False
            else:
                self.write(separator)
            self.visit(node)

    def write_suite(self, nodes):
        with self.add_indentation():
            for line in nodes:
                self.visit(line)

    @contextmanager
    def add_indentation(self):
        self.indentation += 4
        try:
            yield
        finally:
            self.indentation -= 4

    @contextmanager
    def parenthesize_if(self, condition):
        if condition:
            self.write('(')
            yield
            self.write(')')
        else:
            yield

    def generic_visit(self, node):
        raise NotImplementedError('missing visit method for %r' % node)

    def visit_Module(self, node):
        for line in node.body:
            self.visit(line)

    visit_Interactive = visit_Module

    def visit_Expression(self, node):
        self.visit(node.body)

    # Multi-line statements

    def visit_FunctionDef(self, node):
        self.write('\n')
        for decorator in node.decorator_list:
            self.write_indentation()
            self.write('@')
            self.visit(decorator)
            self.write('\n')

        self.write_indentation()
        self.write('def %s(' % node.name)
        self.visit(node.args)
        self.write('):\n')

        self.write_suite(node.body)

    def visit_ClassDef(self, node):
        self.write('\n\n')
        for decorator in node.decorator_list:
            self.write_indentation()
            self.write('@')
            self.visit(decorator)
            self.write('\n')

        self.write_indentation()
        self.write('class %s(' % node.name)
        self.write_expression_list(node.bases)
        self.write('):\n')
        self.write_suite(node.body)

    def visit_For(self, node):
        self.write_indentation()
        self.write('for ')
        self.visit(node.target)
        self.write(' in ')
        self.visit(node.iter)
        self.write(':\n')
        self.write_suite(node.body)
        self.write_else(node.orelse)

    def visit_While(self, node):
        self.write_indentation()
        self.write('while ')
        self.visit(node.test)
        self.write(':\n')
        self.write_suite(node.body)
        self.write_else(node.orelse)

    def visit_If(self, node):
        self.write_indentation()
        self.write('if ')
        self.visit(node.test)
        self.write(':\n')
        self.write_suite(node.body)
        self.write_else(node.orelse)

    def write_else(self, orelse):
        if orelse:
            self.write_indentation()
            self.write('else:\n')
            self.write_suite(orelse)

    def visit_With(self, node):
        self.write_indentation()
        self.write('with ')
        self.visit(node.context_expr)
        if node.optional_vars:
            self.write(' as ')
            self.visit(node.optional_vars)
        self.write(':\n')
        self.write_suite(node.body)

    def visit_TryExcept(self, node):
        self.write_indentation()
        self.write('try:\n')
        self.write_suite(node.body)
        for handler in node.handlers:
            self.write_indentation()
            self.write('except')
            if handler.type:
                self.write(' ')
                self.visit(handler.type)
                if handler.name:
                    self.write(' as ')
                    self.visit(handler.name)
            self.write(':\n')
            self.write_suite(handler.body)
        self.write_else(node.orelse)

    def visit_TryFinally(self, node):
        self.write_indentation()
        self.write('try:\n')
        self.write_suite(node.body)
        self.write_indentation()
        self.write('finally:\n')
        self.write_suite(node.finalbody)

    # One-line statements

    def visit_Return(self, node):
        self.write_indentation()
        self.write('return')
        if node.value:
            self.write(' ')
            self.visit(node.value)
        self.write('\n')

    def visit_Delete(self, node):
        self.write_indentation()
        self.write('del ')
        self.write_expression_list(node.targets)
        self.write('\n')

    def visit_Assign(self, node):
        self.write_indentation()
        self.write_expression_list(node.targets, separator=' = ')
        self.write(' = ')
        self.visit(node.value)
        self.write('\n')

    def visit_AugAssign(self, node):
        self.write_indentation()
        self.visit(node.target)
        self.visit(node.op)
        self.write('= ')
        self.visit(node.value)
        self.write('\n')

    def visit_Print(self, node):
        self.write_indentation()
        self.write('print')
        if node.dest:
            self.write(' >>')
            self.visit(node.dest)
            if node.values:
                self.write(',')
        if node.values:
            self.write(' ')
        self.write_expression_list(node.values)
        if not node.nl:
            self.write(',')
        self.write('\n')

    def visit_Raise(self, node):
        self.write_indentation()
        self.write('raise')
        expressions = [child for child in (node.type, node.inst, node.tback) if child]
        if expressions:
            self.write(' ')
            self.write_expression_list(expressions)
        self.write('\n')

    def visit_Assert(self, node):
        self.write_indentation()
        self.write('assert ')
        self.visit(node.test)
        if node.msg:
            self.write(', ')
            self.visit(node.msg)
        self.write('\n')

    def visit_Import(self, node):
        self.write_indentation()
        self.write('import ')
        self.write_expression_list(node.names)
        self.write('\n')

    def visit_ImportFrom(self, node):
        self.write_indentation()
        self.write('from %s' % ('.' * (node.level or 0)))
        if node.module:
            self.write(node.module)
        self.write(' import ')
        self.write_expression_list(node.names)
        self.write('\n')

    def visit_Exec(self, node):
        self.write_indentation()
        self.write('exec ')
        self.visit(node.body)
        if node.globals:
            self.write(' in ')
            self.visit(node.globals)
        if node.locals:
            self.write(', ')
            self.visit(node.locals)
        self.write('\n')

    def visit_Global(self, node):
        self.write_indentation()
        self.write('global %s\n' % ', '.join(node.names))

    def visit_Expr(self, node):
        self.write_indentation()
        self.visit(node.value)
        self.write('\n')

    def visit_Pass(self, node):
        self.write_indentation()
        self.write('pass\n')

    def visit_Break(self, node):
        self.write_indentation()
        self.write('break\n')

    def visit_Continue(self, node):
        self.write_indentation()
        self.write('continue\n')

    # Expressions

    def visit_BoolOp(self, node):
        my_prec = self.precedence_of_node(node)
        parent_prec = self.precedence_of_node(self.node_stack[-2])
        with self.parenthesize_if(my_prec <= parent_prec):
            op = 'and' if isinstance(node.op, ast.And) else 'or'
            self.write_expression_list(node.values, separator=' %s ' % op)

    def visit_BinOp(self, node):
        parent_node = self.node_stack[-2]
        my_prec = self.precedence_of_node(node)
        parent_prec = self.precedence_of_node(parent_node)
        if my_prec < parent_prec:
            should_parenthesize = True
        elif my_prec == parent_prec:
            if isinstance(node.op, ast.Pow):
                should_parenthesize = node == parent_node.left
            else:
                should_parenthesize = node == parent_node.right
        else:
            should_parenthesize = False

        with self.parenthesize_if(should_parenthesize):
            self.visit(node.left)
            self.write(' ')
            self.visit(node.op)
            self.write(' ')
            self.visit(node.right)

    def visit_UnaryOp(self, node):
        my_prec = self.precedence_of_node(node)
        parent_prec = self.precedence_of_node(self.node_stack[-2])
        with self.parenthesize_if(my_prec < parent_prec):
            self.visit(node.op)
            self.visit(node.operand)

    def visit_Lambda(self, node):
        should_parenthesize = isinstance(
            self.node_stack[-2],
            (ast.BinOp, ast.UnaryOp, ast.Compare, ast.IfExp, ast.Attribute, ast.Subscript, ast.Call)
        )
        with self.parenthesize_if(should_parenthesize):
            self.write('lambda')
            if node.args.args or node.args.vararg or node.args.kwarg:
                self.write(' ')
            self.visit(node.args)
            self.write(': ')
            self.visit(node.body)

    def visit_IfExp(self, node):
        parent_node = self.node_stack[-2]
        if isinstance(parent_node,
                      (ast.BinOp, ast.UnaryOp, ast.Compare, ast.Attribute, ast.Subscript,
                       ast.Call)):
            should_parenthesize = True
        elif isinstance(parent_node, ast.IfExp) and \
                (node is parent_node.test or node is parent_node.body):
            should_parenthesize = True
        else:
            should_parenthesize = False

        with self.parenthesize_if(should_parenthesize):
            self.visit(node.body)
            self.write(' if ')
            self.visit(node.test)
            self.write(' else ')
            self.visit(node.orelse)

    def visit_Dict(self, node):
        self.write('{')
        seen_one = False
        for key, value in zip(node.keys, node.values):
            if seen_one:
                self.write(', ')
            else:
                seen_one = True
            self.visit(key)
            self.write(': ')
            self.visit(value)
        self.write('}')

    def visit_Set(self, node):
        self.write('{')
        self.write_expression_list(node.elts)
        self.write('}')

    def visit_ListComp(self, node):
        self.visit_comp(node, '[', ']')

    def visit_SetComp(self, node):
        self.visit_comp(node, '{', '}')

    def visit_DictComp(self, node):
        self.write('{')
        self.visit(node.key)
        self.write(': ')
        self.visit(node.value)
        for comprehension in node.generators:
            self.visit(comprehension)
        self.write('}')

    def visit_GeneratorExp(self, node):
        self.visit_comp(node, '(', ')')

    def visit_comp(self, node, start, end):
        self.write(start)
        self.visit(node.elt)
        for comprehension in node.generators:
            self.visit(comprehension)
        self.write(end)

    def visit_Yield(self, node):
        with self.parenthesize_if(
                not isinstance(self.node_stack[-2], (ast.Expr, ast.Assign, ast.AugAssign))):
            self.write('yield')
            if node.value:
                self.write(' ')
                self.visit(node.value)

    def visit_Compare(self, node):
        my_prec = self.precedence_of_node(node)
        parent_prec = self.precedence_of_node(self.node_stack[-2])
        with self.parenthesize_if(my_prec <= parent_prec):
            self.visit(node.left)
            for op, expr in zip(node.ops, node.comparators):
                self.write(' ')
                self.visit(op)
                self.write(' ')
                self.visit(expr)

    def visit_Call(self, node):
        self.visit(node.func)
        self.write('(')

        written_something = False
        args = node.args + node.keywords
        if args:
            written_something = True
            self.write_expression_list(args)

        if node.starargs:
            if written_something:
                self.write(', ')
            else:
                written_something = True
            self.write('*')
            self.visit(node.starargs)
        if node.kwargs:
            if written_something:
                self.write(', ')
            self.write('**')
            self.visit(node.kwargs)

        self.write(')')

    def visit_Repr(self, node):
        self.write('`')
        self.visit(node.value)
        self.write('`')

    def visit_Num(self, node):
        self.write(repr(node.n))

    def visit_Str(self, node):
        self.write(repr(node.s))

    def visit_Attribute(self, node):
        self.visit(node.value)
        self.write('.%s' % node.attr)

    def visit_Subscript(self, node):
        self.visit(node.value)
        self.write('[')
        self.visit(node.slice)
        self.write(']')

    def visit_Name(self, node):
        self.write(node.id)

    def visit_List(self, node):
        self.write('[')
        self.write_expression_list(node.elts)
        self.write(']')

    def visit_Tuple(self, node):
        if not node.elts:
            self.write('()')
        else:
            should_parenthesize = not isinstance(
                self.node_stack[-2],
                (ast.Expr, ast.Assign, ast.AugAssign, ast.Return, ast.Yield, ast.arguments)
            )
            with self.parenthesize_if(should_parenthesize):
                if len(node.elts) == 1:
                    self.visit(node.elts[0])
                    self.write(',')
                else:
                    self.write_expression_list(node.elts)

    # slice

    def visit_Ellipsis(self, node):
        self.write('Ellipsis')

    def visit_Slice(self, node):
        if node.lower:
            self.visit(node.lower)
        self.write(':')
        if node.upper:
            self.visit(node.upper)
        if node.step:
            self.write(':')
            self.visit(node.step)

    def visit_ExtSlice(self, node):
        self.write_expression_list(node.dims)

    def visit_Index(self, node):
        self.visit(node.value)

    # operators
    for op, string in _OP_TO_STR.items():
        exec('def visit_%s(self, node): self.write(%r)' % (op.__name__, string))

    # Other types

    def visit_comprehension(self, node):
        self.write(' for ')
        self.visit(node.target)
        self.write(' in ')
        self.visit(node.iter)
        for expr in node.ifs:
            self.write(' if ')
            self.visit(expr)

    def visit_arguments(self, node):
        num_defaults = len(node.defaults)
        if num_defaults:
            non_default_args = node.args[:-num_defaults]
            default_args = zip(node.args[-num_defaults:], node.defaults)
        else:
            non_default_args = node.args
            default_args = []

        written_something = False
        if non_default_args:
            written_something = True
            self.write_expression_list(non_default_args)

        for name, value in default_args:
            if written_something:
                self.write(', ')
            else:
                written_something = True
            self.visit(name)
            self.write('=')
            self.visit(value)

        if node.vararg:
            if written_something:
                self.write(', ')
            else:
                written_something = True
            self.write('*%s' % node.vararg)
        if node.kwarg:
            if written_something:
                self.write(', ')
            self.write('**%s' % node.kwarg)

    def visit_keyword(self, node):
        self.write(node.arg + '=')
        self.visit(node.value)

    def visit_alias(self, node):
        self.write(node.name)
        if node.asname is not None:
            self.write(' as %s' % node.asname)
