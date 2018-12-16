# coding: utf-8
from .tests import check, skip_before


@skip_before((3, 5))
def test_MatMult():
    check('a @ b')
    check('(a * b) @ c')
    check('a * (b @ c)')
    check('a + (b @ c)')


@skip_before((3, 5))
def test_AsyncFunctionDef():
    check('''
async def f(a, b):
    pass
''')


@skip_before((3, 6))
def test_async_gen():
    check('''
async def f():
    yield
''')


@skip_before((3, 6))
def test_async_comprehensions():
    check('''
async def f(lst):
    return [await x for x in lst]
''')


@skip_before((3, 0))
def test_annotations():
    # TODO test precedence
    check('''
def f(a: int, b: str) -> float:
    pass
''')


@skip_before((3, 0))
def test_class_keywords():
    check('''
class Foo(a=3):
    pass
''')
    check('''
class WithMeta(metaclass=type):
    pass
''')


@skip_before((3, 5))
def test_AsyncFor():
    check('''
async def f(y):
    async for x in y:
        pass
''')


@skip_before((3, 0))
def test_py3_with():
    check('''
with a as b:
    pass
''')
    check('''
with a as b, c as d:
    pass
''')
    check('''
with a as b:
    with c as d:
        pass
''')


@skip_before((3, 5))
def test_async_with():
    check('''
async def f(a):
    async with a as b:
        pass
''')


@skip_before((3, 0))
def test_raise_with_cause():
    check('''
raise e from ee
''')


@skip_before((3, 0))
def test_Nonlocal():
    check('''
def f(x):
    nonlocal y
''')
    check('''
def f(x):
    nonlocal y, z
''')


@skip_before((3, 5))
def test_Await():
    check('''
async def f(x):
    await x
''')
    check('''
async def f(x):
    1 + await x
''')
    check('''
async def f(x):
    x = await x
''')
    check('''
async def f(x):
    x += await x
''')
    check('''
async def f(x):
    return 3, (await x)
''')


@skip_before((3, 0))
def test_YieldFrom():
    check('yield from x')
    check('1 + (yield from x)')
    check('x = yield from x')
    check('x += yield from x')
    check('return 3, (yield from x)')


@skip_before((3, 6))
def test_FormattedValue():
    check('f"a"')
    check('f"{b}"')
    check('f"{b}a"')
    check('f"{b!r}"')
    check('f"{b:a}"')
    check('f"{b!r:a}"')
    check('f"{\'b\'!r:\'a\'}"')
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


@skip_before((3, 0))
def test_Bytes():
    check('b"a"')


@skip_before((3, 0))
def test_NameConstant():
    check('True')


@skip_before((3, 0))
def test_Starred():
    check('a, *b = 3')
    check('[a, *b]')


@skip_before((3, 0))
def test_kwonlyargs():
    check('def f(a, *, b): pass')
    check('def f(a, *args, b): pass')
    check('def f(a, *, b=3): pass')
    check('def f(a, *args, b=3): pass')
    check('def f(a, *args, b=3, **kwargs): pass')


@skip_before((3, 6))
def test_annassign():
    check("a: int")
    check("a: int = 3")
    check("(a): int")
    check("""
class A:
    b: int
""")
    check("""
def f():
    a: int
""")
