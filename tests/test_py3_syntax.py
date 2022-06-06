from .tests import check, skip_before, skip_after


@skip_before((3, 5))
def test_MatMult() -> None:
    check("a @ b")
    check("(a * b) @ c")
    check("a * (b @ c)")
    check("a + (b @ c)")


@skip_before((3, 5))
def test_AsyncFunctionDef() -> None:
    check(
        """
async def f(a, b):
    pass
"""
    )


@skip_before((3, 6))
def test_async_gen() -> None:
    check(
        """
async def f():
    yield
"""
    )


@skip_before((3, 6))
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


@skip_before((3, 0))
def test_annotations() -> None:
    # TODO test precedence
    check(
        """
def f(a: int, b: str) -> float:
    pass
"""
    )


@skip_before((3, 0))
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


@skip_before((3, 0))
def test_annotations() -> None:
    check("def f(a: int, b: int = 0, *args: int, c: int, **kwargs: int): pass")


@skip_before((3, 5))
def test_AsyncFor() -> None:
    check(
        """
async def f(y):
    async for x in y:
        pass
"""
    )


@skip_before((3, 0))
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


@skip_before((3, 5))
def test_async_with() -> None:
    check(
        """
async def f(a):
    async with a as b:
        pass
"""
    )


@skip_before((3, 0))
def test_raise_with_cause() -> None:
    check(
        """
raise e from ee
"""
    )


@skip_before((3, 0))
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


@skip_before((3, 5))
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


@skip_before((3, 0))
def test_YieldFrom() -> None:
    check("yield from x")
    check("1 + (yield from x)")
    check("x = yield from x")
    check("x += yield from x")
    check("return 3, (yield from x)")


@skip_before((3, 6))
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
    check(r"f'{a}\n'")
    check(r"f'{a}\t'")
    check("f'{a}é'")
    check('f"{{"')
    check('f"}}"')
    check('f"{{{a}"')


@skip_before((3, 0))
def test_Bytes() -> None:
    check('b"a"')


@skip_before((3, 0))
def test_NameConstant() -> None:
    check("True")


@skip_before((3, 0))
def test_Starred() -> None:
    check("a, *b = 3")
    check("[a, *b]")


@skip_before((3, 0))
def test_kwonlyargs() -> None:
    check("def f(a, *, b): pass")
    check("def f(a, *args, b): pass")
    check("def f(a, *, b=3): pass")
    check("def f(a, *args, b=3): pass")
    check("def f(a, *args, b=3, **kwargs): pass")


@skip_before((3, 6))
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


@skip_before((3, 7))
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


@skip_after((3, 6))
def test_async_varname() -> None:
    check("import async")
    check("await = 3")
    check(
        """
def async(async, await=3):
    return async + await
"""
    )


@skip_before((3, 7))
def test_async_await_in_fstring() -> None:
    check("f'{await x}'")
    check("f'{[x async for x in y]}'")


@skip_before((3, 7))
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


@skip_before((3, 4))
def test_unpacking() -> None:
    check(
        """
def parse(family):
    lastname, *members = family.split()
    return (lastname.upper(), *members)
"""
    )


@skip_before((3, 8))
def test_unparenthesized_unpacking() -> None:
    check(
        """
def parse(family):
    lastname, *members = family.split()
    return lastname.upper(), *members
"""
    )


@skip_before((3, 8))
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


@skip_before((3, 8))
def test_positional_only() -> None:
    check(
        """
def f(x, /):
    pass
"""
    )


@skip_before((3, 8))
def test_fstring_debug_specifier() -> None:
    check("f'{user=} {member_since=}'")
    check("f'{user=!s}  {delta.days=:,d}'")
