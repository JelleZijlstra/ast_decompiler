"""

Implementation of the decompiler class.

"""
import ast
from contextlib import contextmanager
import sys
from typing import Any, Dict, Generator, Iterable, Optional, Type

_OP_TO_STR = {
    ast.Add: "+",
    ast.Sub: "-",
    ast.Mult: "*",
    ast.Div: "/",
    ast.Mod: "%",
    ast.Pow: "**",
    ast.LShift: "<<",
    ast.RShift: ">>",
    ast.BitOr: "|",
    ast.BitXor: "^",
    ast.BitAnd: "&",
    ast.FloorDiv: "//",
    ast.MatMult: "@",
    ast.Invert: "~",
    ast.Not: "not ",
    ast.UAdd: "+",
    ast.USub: "-",
    ast.Eq: "==",
    ast.NotEq: "!=",
    ast.Lt: "<",
    ast.LtE: "<=",
    ast.Gt: ">",
    ast.GtE: ">=",
    ast.Is: "is",
    ast.IsNot: "is not",
    ast.In: "in",
    ast.NotIn: "not in",
    ast.And: "and",
    ast.Or: "or",
}


class _CallArgs(ast.AST):
    """Used as an entry in the precedence table.

    Needed to convey the high precedence of the callee but low precedence of the arguments.

    """

    def __init__(self, args) -> None:
        self.args = args


_PRECEDENCE: Dict[Type[ast.AST], int] = {
    _CallArgs: -1,
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
    ast.MatMult: 9,
    ast.UAdd: 10,
    ast.USub: 10,
    ast.Invert: 10,
    ast.Pow: 11,
    ast.Subscript: 12,
    ast.Call: 12,
    ast.Attribute: 12,
}


def decompile(
    ast: ast.AST,
    indentation: int = 4,
    line_length: int = 100,
    starting_indentation: int = 0,
) -> str:
    """Decompiles an AST into Python code.

    Arguments:
    - ast: code to decompile, using AST objects as generated by the standard library ast module
    - indentation: indentation level of lines
    - line_length: if lines become longer than this length, ast_decompiler will try to break them up
      (but it will not necessarily succeed in all cases)
    - starting_indentation: indentation level at which to start producing code

    """
    decompiler = Decompiler(
        indentation=indentation,
        line_length=line_length,
        starting_indentation=starting_indentation,
    )
    return decompiler.run(ast)


class Decompiler(ast.NodeVisitor):
    def __init__(self, indentation, line_length, starting_indentation) -> None:
        self.lines = []
        self.current_line = []
        self.current_indentation = starting_indentation
        self.node_stack = []
        self.indentation = indentation
        self.max_line_length = line_length
        self.has_unicode_literals = False

    def run(self, ast: ast.AST) -> str:
        self.visit(ast)
        if self.current_line:
            self.lines.append("".join(self.current_line))
            self.current_line = []
        return "".join(self.lines)

    def visit(self, node: ast.AST) -> None:
        self.node_stack.append(node)
        try:
            super().visit(node)
        finally:
            if self.node_stack:
                self.node_stack.pop()

    def precedence_of_node(self, node: Optional[ast.AST]) -> int:
        if node is None:
            return -1
        if isinstance(node, (ast.BinOp, ast.UnaryOp, ast.BoolOp)):
            return _PRECEDENCE[type(node.op)]
        return _PRECEDENCE.get(type(node), -1)

    def get_parent_node(self) -> Optional[ast.AST]:
        try:
            return self.node_stack[-2]
        except IndexError:
            return None

    def has_parent_of_type(self, node_type: Type[ast.AST]) -> bool:
        return any(isinstance(parent, node_type) for parent in self.node_stack)

    def write(self, code: str) -> None:
        assert isinstance(code, str), f"invalid code {code!r}"
        self.current_line.append(code)

    def write_indentation(self) -> None:
        self.write(" " * self.current_indentation)

    def write_newline(self) -> None:
        line = "".join(self.current_line) + "\n"
        self.lines.append(line)
        self.current_line = []

    def current_line_length(self) -> int:
        return sum(map(len, self.current_line))

    def write_expression_list(
        self,
        nodes,
        separator=", ",
        allow_newlines=True,
        need_parens=True,
        final_separator_if_multiline=True,
    ) -> None:
        """Writes a list of nodes, separated by separator.

        If allow_newlines, will write the expression over multiple lines if necessary to say within
        max_line_length. If need_parens, will surround the expression with parentheses in this case.
        If final_separator_if_multiline, will write a separator at the end of the list if it is
        divided over multiple lines.

        """
        first = True
        last_line = len(self.lines)
        current_line = list(self.current_line)
        for node in nodes:
            if first:
                first = False
            else:
                self.write(separator)
            self.visit(node)
            if allow_newlines and (
                self.current_line_length() > self.max_line_length
                or last_line != len(self.lines)
            ):
                break
        else:
            return  # stayed within the limit

        # reset state
        del self.lines[last_line:]
        self.current_line = current_line

        separator = separator.rstrip()
        if need_parens:
            self.write("(")
        self.write_newline()
        with self.add_indentation():
            num_nodes = len(nodes)
            for i, node in enumerate(nodes):
                self.write_indentation()
                self.visit(node)
                if final_separator_if_multiline or i < num_nodes - 1:
                    self.write(separator)
                self.write_newline()

        self.write_indentation()
        if need_parens:
            self.write(")")

    def write_suite(self, nodes: Iterable[ast.AST]) -> None:
        with self.add_indentation():
            for line in nodes:
                self.visit(line)

    @contextmanager
    def add_indentation(self) -> Generator[None, None, None]:
        self.current_indentation += self.indentation
        try:
            yield
        finally:
            self.current_indentation -= self.indentation

    @contextmanager
    def parenthesize_if(self, condition: bool) -> Generator[None, None, None]:
        if condition:
            self.write("(")
            yield
            self.write(")")
        else:
            yield

    @contextmanager
    def f_literalise_if(self, condition: bool) -> Generator[None, None, None]:
        if condition:
            self.write("f'")
            yield
            self.write("'")
        else:
            yield

    def generic_visit(self, node):
        raise NotImplementedError("missing visit method for %r" % node)

    def visit_Module(self, node) -> None:
        for line in node.body:
            self.visit(line)

    visit_Interactive = visit_Module

    def visit_Expression(self, node) -> None:
        self.visit(node.body)

    # Multi-line statements

    def visit_FunctionDef(self, node) -> None:
        self.write_function_def(node)

    def visit_AsyncFunctionDef(self, node) -> None:
        self.write_function_def(node, is_async=True)

    def write_function_def(self, node, is_async=False) -> None:
        self.write_newline()
        for decorator in node.decorator_list:
            self.write_indentation()
            self.write("@")
            self.visit(decorator)
            self.write_newline()

        self.write_indentation()
        if is_async:
            self.write("async ")
        self.write("def %s(" % node.name)
        self.visit(node.args)
        self.write(")")
        if getattr(node, "returns", None):
            self.write(" -> ")
            self.visit(node.returns)
        self.write(":")
        self.write_newline()

        self.write_suite(node.body)

    def visit_ClassDef(self, node) -> None:
        self.write_newline()
        self.write_newline()
        for decorator in node.decorator_list:
            self.write_indentation()
            self.write("@")
            self.visit(decorator)
            self.write_newline()

        self.write_indentation()
        self.write("class %s(" % node.name)
        exprs = node.bases + getattr(node, "keywords", [])
        self.write_expression_list(exprs, need_parens=False)
        self.write("):")
        self.write_newline()
        self.write_suite(node.body)

    def visit_For(self, node) -> None:
        self.write_for(node)

    def visit_AsyncFor(self, node) -> None:
        self.write_for(node, is_async=True)

    def write_for(self, node, is_async=False) -> None:
        self.write_indentation()
        if is_async:
            self.write("async ")
        self.write("for ")
        self.visit(node.target)
        self.write(" in ")
        self.visit(node.iter)
        self.write(":")
        self.write_newline()
        self.write_suite(node.body)
        self.write_else(node.orelse)

    def visit_While(self, node) -> None:
        self.write_indentation()
        self.write("while ")
        self.visit(node.test)
        self.write(":")
        self.write_newline()
        self.write_suite(node.body)
        self.write_else(node.orelse)

    def visit_If(self, node) -> None:
        self.write_indentation()
        self.write("if ")
        self.visit(node.test)
        self.write(":")
        self.write_newline()
        self.write_suite(node.body)
        while (
            node.orelse and len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If)
        ):
            node = node.orelse[0]
            self.write_indentation()
            self.write("elif ")
            self.visit(node.test)
            self.write(":")
            self.write_newline()
            self.write_suite(node.body)
        self.write_else(node.orelse)

    def write_else(self, orelse) -> None:
        if orelse:
            self.write_indentation()
            self.write("else:")
            self.write_newline()
            self.write_suite(orelse)

    def visit_AsyncWith(self, node) -> None:
        self.visit_With(node, is_async=True)

    def visit_With(self, node, is_async=False) -> None:
        self.write_indentation()
        if is_async:
            self.write("async ")
        self.write("with ")
        self.write_expression_list(node.items, allow_newlines=False)
        self.write(":")
        self.write_newline()
        self.write_suite(node.body)

    def visit_withitem(self, node) -> None:
        self.visit(node.context_expr)
        if node.optional_vars:
            self.write(" as ")
            self.visit(node.optional_vars)

    def visit_Try(self, node) -> None:
        self.write_indentation()
        self.write("try:")
        self.write_newline()
        self.write_suite(node.body)
        for handler in node.handlers:
            self.visit(handler)
        self.write_else(node.orelse)
        if node.finalbody:
            self.write_finalbody(node.finalbody)

    def write_finalbody(self, body) -> None:
        self.write_indentation()
        self.write("finally:")
        self.write_newline()
        self.write_suite(body)

    # One-line statements

    def visit_Return(self, node) -> None:
        self.write_indentation()
        self.write("return")
        if node.value:
            self.write(" ")
            self.visit(node.value)
        self.write_newline()

    def visit_Delete(self, node) -> None:
        self.write_indentation()
        self.write("del ")
        self.write_expression_list(node.targets, allow_newlines=False)
        self.write_newline()

    def visit_Assign(self, node) -> None:
        self.write_indentation()
        self.write_expression_list(node.targets, separator=" = ", allow_newlines=False)
        self.write(" = ")
        self.visit(node.value)
        self.write_newline()

    def visit_AugAssign(self, node) -> None:
        self.write_indentation()
        self.visit(node.target)
        self.write(" ")
        self.visit(node.op)
        self.write("= ")
        self.visit(node.value)
        self.write_newline()

    def visit_AnnAssign(self, node) -> None:
        self.write_indentation()
        if not node.simple:
            self.write("(")
        self.visit(node.target)
        if not node.simple:
            self.write(")")
        self.write(": ")
        self.visit(node.annotation)
        if node.value is not None:
            self.write(" = ")
            self.visit(node.value)
        self.write_newline()

    def visit_Print(self, node) -> None:
        self.write_indentation()
        self.write("print")
        if node.dest:
            self.write(" >>")
            self.visit(node.dest)
            if node.values:
                self.write(",")
        if node.values:
            self.write(" ")
        self.write_expression_list(node.values, allow_newlines=False)
        if not node.nl:
            self.write(",")
        self.write_newline()

    def visit_Raise(self, node) -> None:
        self.write_indentation()
        self.write("raise")
        if node.exc is not None:
            self.write(" ")
            self.visit(node.exc)
            if node.cause is not None:
                self.write(" from ")
                self.visit(node.cause)
        self.write_newline()

    def visit_Assert(self, node) -> None:
        self.write_indentation()
        self.write("assert ")
        self.visit(node.test)
        if node.msg:
            self.write(", ")
            self.visit(node.msg)
        self.write_newline()

    def visit_Import(self, node) -> None:
        self.write_indentation()
        self.write("import ")
        self.write_expression_list(node.names, allow_newlines=False)
        self.write_newline()

    def visit_ImportFrom(self, node) -> None:
        if node.module == "__future__" and any(
            alias.name == "unicode_literals" for alias in node.names
        ):
            self.has_unicode_literals = True

        self.write_indentation()
        self.write("from %s" % ("." * (node.level or 0)))
        if node.module:
            self.write(node.module)
        self.write(" import ")
        self.write_expression_list(node.names)
        self.write_newline()

    def visit_Exec(self, node) -> None:
        self.write_indentation()
        self.write("exec ")
        self.visit(node.body)
        if node.globals:
            self.write(" in ")
            self.visit(node.globals)
        if node.locals:
            self.write(", ")
            self.visit(node.locals)
        self.write_newline()

    def visit_Global(self, node) -> None:
        self.write_indentation()
        self.write("global %s" % ", ".join(node.names))
        self.write_newline()

    def visit_Nonlocal(self, node) -> None:
        self.write_indentation()
        self.write("nonlocal %s" % ", ".join(node.names))
        self.write_newline()

    def visit_Expr(self, node) -> None:
        self.write_indentation()
        self.visit(node.value)
        self.write_newline()

    def visit_Pass(self, node) -> None:
        self.write_indentation()
        self.write("pass")
        self.write_newline()

    def visit_Break(self, node) -> None:
        self.write_indentation()
        self.write("break")
        self.write_newline()

    def visit_Continue(self, node) -> None:
        self.write_indentation()
        self.write("continue")
        self.write_newline()

    # Expressions

    def visit_BoolOp(self, node) -> None:
        my_prec = self.precedence_of_node(node)
        parent_prec = self.precedence_of_node(self.get_parent_node())
        with self.parenthesize_if(my_prec <= parent_prec):
            op = "and" if isinstance(node.op, ast.And) else "or"
            self.write_expression_list(
                node.values,
                separator=" %s " % op,
                final_separator_if_multiline=False,
            )

    def visit_BinOp(self, node) -> None:
        parent_node = self.get_parent_node()
        my_prec = self.precedence_of_node(node)
        parent_prec = self.precedence_of_node(parent_node)
        if my_prec < parent_prec:
            should_parenthesize = True
        elif my_prec == parent_prec and isinstance(parent_node, ast.BinOp):
            if isinstance(node.op, ast.Pow):
                should_parenthesize = node == parent_node.left
            else:
                should_parenthesize = node == parent_node.right
        else:
            should_parenthesize = False

        with self.parenthesize_if(should_parenthesize):
            self.visit(node.left)
            self.write(" ")
            self.visit(node.op)
            self.write(" ")
            self.visit(node.right)

    def visit_UnaryOp(self, node) -> None:
        my_prec = self.precedence_of_node(node)
        parent_prec = self.precedence_of_node(self.get_parent_node())
        with self.parenthesize_if(my_prec < parent_prec):
            self.visit(node.op)
            self.visit(node.operand)

    def visit_Lambda(self, node) -> None:
        should_parenthesize = isinstance(
            self.get_parent_node(),
            (
                ast.BinOp,
                ast.UnaryOp,
                ast.Compare,
                ast.IfExp,
                ast.Attribute,
                ast.Subscript,
                ast.Call,
                ast.BoolOp,
            ),
        )
        with self.parenthesize_if(should_parenthesize):
            self.write("lambda")
            if node.args.args or node.args.vararg or node.args.kwarg:
                self.write(" ")
            self.visit(node.args)
            self.write(": ")
            self.visit(node.body)

    def visit_NamedExpr(self, node) -> None:
        self.write("(")
        self.visit(node.target)
        self.write(" := ")
        # := has the lowest precedence, so we should never need to parenthesize this
        self.visit(node.value)
        self.write(")")

    def visit_IfExp(self, node) -> None:
        parent_node = self.get_parent_node()
        if isinstance(
            parent_node,
            (
                ast.BinOp,
                ast.UnaryOp,
                ast.Compare,
                ast.Attribute,
                ast.Subscript,
                ast.Call,
                ast.BoolOp,
                ast.comprehension,
            ),
        ):
            should_parenthesize = True
        elif isinstance(parent_node, ast.IfExp) and (
            node is parent_node.test or node is parent_node.body
        ):
            should_parenthesize = True
        else:
            should_parenthesize = False

        with self.parenthesize_if(should_parenthesize):
            self.visit(node.body)
            self.write(" if ")
            self.visit(node.test)
            self.write(" else ")
            self.visit(node.orelse)

    def visit_Dict(self, node) -> None:
        self.write("{")
        items = [KeyValuePair(key, value) for key, value in zip(node.keys, node.values)]
        self.write_expression_list(items, need_parens=False)
        self.write("}")

    def visit_KeyValuePair(self, node) -> None:
        self.visit(node.key)
        self.write(": ")
        self.visit(node.value)

    def visit_Set(self, node) -> None:
        self.write("{")
        self.write_expression_list(node.elts, need_parens=False)
        self.write("}")

    def visit_ListComp(self, node) -> None:
        self.visit_comp(node, "[", "]")

    def visit_SetComp(self, node) -> None:
        self.visit_comp(node, "{", "}")

    def visit_DictComp(self, node) -> None:
        self.write("{")
        elts = [KeyValuePair(node.key, node.value)] + node.generators
        self.write_expression_list(elts, separator=" ", need_parens=False)
        self.write("}")

    def visit_GeneratorExp(self, node) -> None:
        parent_node = self.get_parent_node()
        # if this is the only argument to a function, omit the extra parentheses
        if (
            isinstance(parent_node, _CallArgs)
            and len(parent_node.args) == 1
            and node == parent_node.args[0]
        ):
            start = end = ""
        else:
            start = "("
            end = ")"
        self.visit_comp(node, start, end)

    def visit_comp(self, node, start, end) -> None:
        self.write(start)
        self.write_expression_list(
            [node.elt] + node.generators, separator=" ", need_parens=False
        )
        self.write(end)

    def visit_Await(self, node) -> None:
        with self.parenthesize_if(
            not isinstance(
                self.get_parent_node(), (ast.Expr, ast.Assign, ast.AugAssign)
            )
        ):
            self.write("await ")
            self.visit(node.value)

    def visit_Yield(self, node) -> None:
        with self.parenthesize_if(
            not isinstance(
                self.get_parent_node(), (ast.Expr, ast.Assign, ast.AugAssign)
            )
        ):
            self.write("yield")
            if node.value:
                self.write(" ")
                self.visit(node.value)

    def visit_YieldFrom(self, node) -> None:
        with self.parenthesize_if(
            not isinstance(
                self.get_parent_node(), (ast.Expr, ast.Assign, ast.AugAssign)
            )
        ):
            self.write("yield from ")
            self.visit(node.value)

    def visit_Compare(self, node) -> None:
        my_prec = self.precedence_of_node(node)
        parent_prec = self.precedence_of_node(self.get_parent_node())
        with self.parenthesize_if(my_prec <= parent_prec):
            self.visit(node.left)
            for op, expr in zip(node.ops, node.comparators):
                self.write(" ")
                self.visit(op)
                self.write(" ")
                self.visit(expr)

    def visit_Call(self, node: ast.Call) -> None:
        self.visit(node.func)
        self.write("(")

        args = node.args + node.keywords
        self.node_stack.append(_CallArgs(args))
        try:
            if args:
                self.write_expression_list(
                    args,
                    need_parens=False,
                    final_separator_if_multiline=False,  # it's illegal after *args and **kwargs
                )

            self.write(")")
        finally:
            self.node_stack.pop()

    def visit_StarArg(self, node) -> None:
        self.write("*")
        self.visit(node.arg)

    def visit_DoubleStarArg(self, node) -> None:
        self.write("**")
        self.visit(node.arg)

    def visit_KeywordArg(self, node) -> None:
        self.visit(node.arg)
        if node.value is not None:
            self.write("=")
            self.visit(node.value)

    def visit_Repr(self, node) -> None:
        self.write("`")
        self.visit(node.value)
        self.write("`")

    def visit_Num(self, node) -> None:
        self.write_number(node.n)

    def write_number(self, number) -> None:
        should_parenthesize = (
            isinstance(number, int)
            and number >= 0
            and isinstance(self.get_parent_node(), ast.Attribute)
        )
        if not should_parenthesize:
            should_parenthesize = (
                isinstance(number, complex)
                and number.real == 0.0
                and (number.imag < 0 or number.imag == -0.0)
            )
        if not should_parenthesize and (isinstance(number, complex) or number < 0):
            parent_node = self.get_parent_node()
            should_parenthesize = (
                isinstance(parent_node, ast.UnaryOp)
                and isinstance(parent_node.op, ast.USub)
                and hasattr(parent_node, "lineno")
            )
        with self.parenthesize_if(should_parenthesize):
            if isinstance(number, float) and abs(number) > sys.float_info.max:
                # otherwise we write inf, which won't be parsed back right
                # I don't know of any way to write nan with a literal
                self.write("1e1000" if number > 0 else "-1e1000")
            elif isinstance(number, (int, float)) and number < 0:
                # needed for precedence to work correctly
                me = self.node_stack.pop()
                if isinstance(number, int):
                    val = str(-number)
                else:
                    val = repr(type(number)(-number))  # - of long may be int
                self.visit(ast.UnaryOp(op=ast.USub(), operand=ast.Name(id=val)))
                self.node_stack.append(me)
            else:
                self.write(repr(number))

    def visit_Str(self, node) -> None:
        self.write_string(node.s, kind=None)

    def write_string(self, string_value, kind=None) -> None:
        if kind is not None:
            self.write(kind)
        if self.has_parent_of_type(ast.FormattedValue):
            delimiter = '"'
        else:
            delimiter = "'"
        self.write(delimiter)
        s = string_value.encode("unicode-escape").decode("ascii")
        self.write(s.replace(delimiter, "\\" + delimiter))
        self.write(delimiter)

    def visit_FormattedValue(self, node):
        has_parent = isinstance(self.get_parent_node(), ast.JoinedStr)
        with self.f_literalise_if(not has_parent):
            self.write("{")
            if isinstance(node.value, ast.JoinedStr):
                raise NotImplementedError(
                    "ast_decompiler does not support nested f-strings yet"
                )
            add_space = isinstance(
                node.value, (ast.Set, ast.Dict, ast.SetComp, ast.DictComp)
            )
            if add_space:
                self.write(" ")
            self.visit(node.value)
            if node.conversion != -1:
                self.write("!%s" % chr(node.conversion))
            if node.format_spec is not None:
                self.write(":")
                if isinstance(node.format_spec, ast.JoinedStr):
                    self.visit(node.format_spec)
                elif isinstance(node.format_spec, ast.Str):
                    self.write(node.format_spec.s)
                else:
                    raise TypeError(
                        "format spec must be a string, not {}".format(node.format_spec)
                    )
            if add_space:
                self.write(" ")
            self.write("}")

    def visit_JoinedStr(self, node) -> None:
        has_parent = isinstance(self.get_parent_node(), ast.FormattedValue)
        with self.f_literalise_if(not has_parent):
            for value in node.values:
                if isinstance(value, ast.Str):
                    # always escape '
                    self.write(
                        value.s.encode("unicode-escape")
                        .decode("ascii")
                        .replace("'", r"\'")
                    )
                else:
                    self.visit(value)

    def visit_Bytes(self, node) -> None:
        self.write(repr(node.s))

    def visit_NameConstant(self, node) -> None:
        self.write(repr(node.value))

    def visit_Constant(self, node):
        if node.value is Ellipsis:
            self.write("...")
        elif isinstance(node.value, str):
            self.write_string(node.value, node.kind)
        elif isinstance(node.value, bytes):
            self.write(repr(node.value))
        elif isinstance(node.value, (int, float, complex)):
            self.write_number(node.value)
        elif isinstance(node.value, (bool, type(None))):
            self.write(repr(node.value))
        else:
            raise NotImplementedError(ast.dump(node))

    def visit_Attribute(self, node) -> None:
        self.visit(node.value)
        self.write(".%s" % node.attr)

    def visit_Subscript(self, node) -> None:
        self.visit(node.value)
        self.write("[")
        self.visit(node.slice)
        self.write("]")

    def visit_Starred(self, node) -> None:
        # TODO precedence
        self.write("*")
        self.visit(node.value)

    def visit_Name(self, node) -> None:
        self.write(node.id)

    def visit_List(self, node) -> None:
        self.write("[")
        self.write_expression_list(node.elts, need_parens=False)
        self.write("]")

    def visit_Tuple(self, node) -> None:
        if not node.elts:
            self.write("()")
        else:
            parent_node = self.get_parent_node()
            allow_parens = True
            should_parenthesize = not isinstance(
                parent_node,
                (ast.Expr, ast.Assign, ast.AugAssign, ast.Return, ast.Yield),
            )
            if (
                isinstance(parent_node, ast.comprehension)
                and node is parent_node.target
            ):
                should_parenthesize = False
            # Only relevant on 3.9+, where the ExtSlice class no longer exists.
            if isinstance(parent_node, ast.Subscript) and node is parent_node.slice:
                should_parenthesize = False
                allow_parens = False
            # https://bugs.python.org/issue32117
            if (
                hasattr(ast, "Starred")
                and isinstance(parent_node, (ast.Return, ast.Yield))
                and any(isinstance(elt, ast.Starred) for elt in node.elts)
                and sys.version_info < (3, 8)
            ):
                should_parenthesize = True
            with self.parenthesize_if(should_parenthesize):
                if len(node.elts) == 1:
                    self.visit(node.elts[0])
                    self.write(",")
                else:
                    self.write_expression_list(
                        node.elts, need_parens=allow_parens and not should_parenthesize
                    )

    # slice

    def visit_Ellipsis(self, node) -> None:
        self.write("...")

    def visit_Slice(self, node) -> None:
        if node.lower:
            self.visit(node.lower)
        self.write(":")
        if node.upper:
            self.visit(node.upper)
        if node.step:
            self.write(":")
            self.visit(node.step)

    if sys.version_info < (3, 9):

        # Any to avoid version-dependent errors from pyanalyze.
        def visit_ExtSlice(self, node: Any) -> None:
            if len(node.dims) == 1:
                self.visit(node.dims[0])
                self.write(",")
            else:
                self.write_expression_list(node.dims, need_parens=False)

        def visit_Index(self, node: Any) -> None:
            self.visit(node.value)

    # operators
    for op, string in _OP_TO_STR.items():
        exec("def visit_%s(self, node): self.write(%r)" % (op.__name__, string))

    # Other types

    visit_Load = (
        visit_Store
    ) = (
        visit_Del
    ) = visit_AugLoad = visit_AugStore = visit_Param = lambda self, node: None

    def visit_comprehension(self, node) -> None:
        if getattr(node, "is_async", False):
            self.write("async ")
        self.write("for ")
        self.visit(node.target)
        self.write(" in ")
        self.visit(node.iter)
        for expr in node.ifs:
            self.write(" if ")
            self.visit(expr)

    def visit_ExceptHandler(self, node) -> None:
        self.write_indentation()
        self.write("except")
        if node.type:
            self.write(" ")
            self.visit(node.type)
            if node.name:
                self.write(" as ")
                self.write(node.name)
        self.write(":")
        self.write_newline()
        self.write_suite(node.body)

    def visit_arguments(self, node) -> None:
        args = []
        if hasattr(node, "posonlyargs") and node.posonlyargs:
            args += node.posonlyargs
            args.append(ast.Name(id="/"))

        num_defaults = len(node.defaults)
        if num_defaults:
            args += node.args[:-num_defaults]
            default_args = zip(node.args[-num_defaults:], node.defaults)
        else:
            args += list(node.args)
            default_args = []
        for name, value in default_args:
            args.append(KeywordArg(name, value))

        if node.vararg:
            args.append(StarArg(ast.Name(id=node.vararg.arg)))

        # TODO write a * if there are kwonly args but no vararg
        if hasattr(node, "kw_defaults"):
            if node.kwonlyargs and not node.vararg:
                args.append(StarArg(ast.Name(id="")))
            num_kwarg_defaults = len(node.kw_defaults)
            if num_kwarg_defaults:
                args += node.kwonlyargs[:-num_kwarg_defaults]
                default_kwargs = zip(
                    node.kwonlyargs[-num_kwarg_defaults:], node.kw_defaults
                )
            else:
                args += node.kwonlyargs
                default_kwargs = []
            for name, value in default_kwargs:
                args.append(KeywordArg(name, value))

        if node.kwarg:
            args.append(DoubleStarArg(ast.Name(id=node.kwarg.arg)))

        if args:
            # lambdas can't have a multiline arglist
            allow_newlines = not isinstance(self.get_parent_node(), ast.Lambda)
            self.write_expression_list(
                args,
                allow_newlines=allow_newlines,
                need_parens=False,
                final_separator_if_multiline=False,  # illegal after **kwargs
            )

    def visit_arg(self, node) -> None:
        self.write(node.arg)
        if node.annotation:
            self.write(": ")
            # TODO precedence
            self.visit(node.annotation)

    def visit_keyword(self, node) -> None:
        if node.arg is None:
            # in py3, **kwargs is a keyword whose arg is None
            self.write("**")
        else:
            self.write(node.arg + "=")
        self.visit(node.value)

    def visit_alias(self, node) -> None:
        self.write(node.name)
        if node.asname is not None:
            self.write(" as %s" % node.asname)


# helper ast nodes to make decompilation easier
class KeyValuePair(object):
    """A key-value pair as used in a dictionary display."""

    _fields = ["key", "value"]

    def __init__(self, key, value) -> None:
        self.key = key
        self.value = value


class StarArg(object):
    """A * argument."""

    _fields = ["arg"]

    def __init__(self, arg) -> None:
        self.arg = arg


class DoubleStarArg(object):
    """A ** argument."""

    _fields = ["arg"]

    def __init__(self, arg) -> None:
        self.arg = arg


class KeywordArg(object):
    """A x=3 keyword argument in a function definition."""

    _fields = ["arg", "value"]

    def __init__(self, arg, value) -> None:
        self.arg = arg
        self.value = value
