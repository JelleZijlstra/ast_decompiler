import ast

from ast_decompiler import decompile

from .tests import assert_decompiles, check, skip_after, skip_before


def test_MatMult() -> None:
    check("a @ b")
    check("(a * b) @ c")
    check("a * (b @ c)")
    check("a + (b @ c)")


def test_AsyncFunctionDef() -> None:
    check(
        """
async def f(a, b):
    pass
"""
    )


def test_async_gen() -> None:
    check(
        """
async def f():
    yield
"""
    )


def test_async_comprehensions() -> None:
    check(
        """
async def f(lst):
    return [await x for x in lst]
"""
    )
    check(
        """
async def f(lst):
    a = [x async for x in lst]
    b = {x async for x in lst}
    c = {x: x async for x in lst}
    d = (x async for x in lst)
"""
    )


def test_function_annotations() -> None:
    check(
        """
def f(a: int, b: str) -> float:
    pass
"""
    )


def test_class_keywords() -> None:
    check(
        """
class Foo(a=3):
    pass
"""
    )
    check(
        """
class WithMeta(metaclass=type):
    pass
"""
    )


def test_annotations() -> None:
    check("def f(a: int, b: int = 0, *args: int, c: int, **kwargs: int): pass")


def test_AsyncFor() -> None:
    check(
        """
async def f(y):
    async for x in y:
        pass
"""
    )


def test_py3_with() -> None:
    check(
        """
with a as b:
    pass
"""
    )
    check(
        """
with a as b, c as d:
    pass
"""
    )
    check(
        """
with a as b:
    with c as d:
        pass
"""
    )


def test_async_with() -> None:
    check(
        """
async def f(a):
    async with a as b:
        pass
"""
    )


def test_raise_with_cause() -> None:
    check(
        """
raise e from ee
"""
    )


def test_Nonlocal() -> None:
    check(
        """
def f(x):
    nonlocal y
"""
    )
    check(
        """
def f(x):
    nonlocal y, z
"""
    )


def test_Await() -> None:
    check(
        """
async def f(x):
    await x
"""
    )
    check(
        """
async def f(x):
    1 + await x
"""
    )
    check(
        """
async def f(x):
    x = await x
"""
    )
    check(
        """
async def f(x):
    x += await x
"""
    )
    check(
        """
async def f(x):
    return 3, (await x)
"""
    )
    check(
        """
async def f(x, y, z):
    return await (x if y else z)
"""
    )


def test_YieldFrom() -> None:
    check("yield from x")
    check("1 + (yield from x)")
    check("x = yield from x")
    check("x += yield from x")
    check("return 3, (yield from x)")


def test_FormattedValue() -> None:
    check('f"a"')
    check('f"{b}"')
    check('f"{b}a"')
    check('f"{b!r}"')
    check('f"{b:a}"')
    check('f"{b!r:a}"')
    check("f\"{'b'!r:'a'}\"")
    check('f"{a}b{c!a}s"')
    check('f"{a.b}c{d()}"')
    check("f'{1/3:.1f}'")
    check(r"f'{a}\''")
    check("f'{1/3:{5}.1}'")
    check("f'{ {a, b, c} }'")
    check("f'{ {a: b} }'")
    check("f'{ {a for a in b} }'")
    check("f'{ {a: b for a, b in c} }'")
    check("f'{(lambda: 0)}'")
    check(r"f'{a}\n'")
    check(r"f'{a}\t'")
    check("f'{a}é'")
    check('f"{{"')
    check('f"}}"')
    check('f"{{{a}"')


def test_formatted_dict_with_format_spec() -> None:
    check("f\"{ {} :'''}\"")


def test_Bytes() -> None:
    check('b"a"')


def test_NameConstant() -> None:
    check("True")


def test_Starred() -> None:
    check("a, *b = 3")
    check("[a, *b]")
    check("(*(0 <= 0),)")


def test_kwonlyargs() -> None:
    check("def f(a, *, b): pass")
    check("def f(a, *args, b): pass")
    check("def f(a, *, b=3): pass")
    check("def f(a, *args, b=3): pass")
    check("def f(a, *args, b=3, **kwargs): pass")


def test_annassign() -> None:
    check("a: int")
    check("a: int = 3")
    check("(a): int")
    check(
        """
class A:
    b: int
"""
    )
    check(
        """
def f():
    a: int
"""
    )


def test_future_annotations() -> None:
    # This doesn't really affect ast_decompiler because the __future__
    # import doesn't change the AST.
    check(
        """
from __future__ import annotations

def f(x: int) -> str:
    pass

y: float
"""
    )


def test_async_await_in_fstring() -> None:
    check("f'{await x}'")
    check("f'{[x async for x in y]}'")


def test_too_many_args() -> None:
    args = ", ".join(f"x{i}" for i in range(300))
    check(
        """
def f({}):
    pass

f({})
""".format(
            args, args
        )
    )


@skip_after((3, 13))
def test_finally_continue() -> None:
    check(
        """
def f():
    for x in y:
        try:
            whatever
        finally:
            continue
"""
    )


def test_unpacking() -> None:
    check(
        """
def parse(family):
    lastname, *members = family.split()
    return (lastname.upper(), *members)
"""
    )


def test_unparenthesized_unpacking() -> None:
    check(
        """
def parse(family):
    lastname, *members = family.split()
    return lastname.upper(), *members
"""
    )


def test_assignment_expression() -> None:
    # Some of these can be used unparenthesized in 3.10+ but we don't bother.
    check(
        """
if (x := 3):
    pass
{(y := 4)}
{(z := 5) for a in b}
lst[(alpha := 3)]
lst[(beta := 4):(gamma := 5)]
"""
    )


def test_positional_only() -> None:
    check(
        """
def f(x, /):
    pass
"""
    )


def test_fstring_debug_specifier() -> None:
    check("f'{user=} {member_since=}'")
    check("f'{user=!s}  {delta.days=:,d}'")


@skip_before((3, 14))
def test_tstring() -> None:
    check("t'a'")
    check("t'{a}'")
    check("t'{a=}'")
    check("t'{a!a}'")
    check("t'{a!r}'")
    check("t'{a!s}'")
    check("t'{a:b}'")
    check("t'{a:{width}.2f}'")
    check("t'{ {a, b} }'")
    check("t'{ {a: b} }'")
    check("t'{ {a for a in b} }'")
    check("t'{ {a: b for a, b in c} }'")
    check("t'{{'")
    check("t'}}'")
    check("t'{{{a}}}'")
    check("t'{a}é'")


@skip_before((3, 14))
def test_tstring_generated_interpolation() -> None:
    interpolation = ast.Interpolation(
        value=ast.BinOp(
            left=ast.Name(id="a", ctx=ast.Load()),
            op=ast.Add(),
            right=ast.Name(id="b", ctx=ast.Load()),
        ),
        str=None,
        conversion=-1,
    )
    node = ast.Expression(body=ast.TemplateStr(values=[interpolation]))
    assert decompile(node) == "t'{a + b}'"


@skip_before((3, 14))
def test_unparenthesized_except_groups() -> None:
    check(
        """
try:
    pass
except ValueError, TypeError:
    pass
"""
    )
    check(
        """
try:
    pass
except* ValueError, TypeError:
    pass
"""
    )


@skip_before((3, 15))
def test_lazy_imports() -> None:
    check("lazy import json")
    check("lazy import json as js, os.path")
    check("lazy from json import dumps, loads as l")
    check("lazy from . import sibling")
    check("lazy from ..pkg import item as alias")


@skip_before((3, 15))
def test_unpacking_comprehensions() -> None:
    check("[*it for it in its]")
    check("[*(x if x else y) for x in xs]")
    check("[*item for row in rows if row for item in row]")
    check("{*it for it in its}")
    check("{*(x if x else y) for x in xs}")
    check("{**d for d in dicts}")
    check("{**(x if x else y) for x in xs}")
    check("(*it for it in its)")
    check("(*(y := [i, i + 1]) for i in its)")
    check("f(*it for it in its)")


@skip_before((3, 15))
def test_async_unpacking_comprehensions() -> None:
    check(
        """
async def f(xs):
    a = [*x async for x in xs]
    b = {*x async for x in xs}
    c = {**x async for x in xs}
    d = (*x async for x in xs)
"""
    )
