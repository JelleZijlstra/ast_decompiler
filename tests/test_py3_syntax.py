from tests import check, only_on_version


@only_on_version(3)
def test_MatMult():
    check('a @ b')
    check('(a * b) @ c')
    check('a * (b @ c)')
    check('a + (b @ c)')


@only_on_version(3)
def test_AsyncFunctionDef():
    check('''
async def f(a, b):
    pass
''')


@only_on_version(3)
def test_annotations():
    # TODO test precedence
    check('''
def f(a: int, b: str) -> float:
    pass
''')


@only_on_version(3)
def test_class_keywords():
    check('''
class Foo(a=3):
    pass
''')
    check('''
class WithMeta(metaclass=type):
    pass
''')


@only_on_version(3)
def test_AsyncFor():
    check('''
async def f(y):
    async for x in y:
        pass
''')


@only_on_version(3)
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


@only_on_version(3)
def test_async_with():
    check('''
async def f(a):
    async with a as b:
        pass
''')


@only_on_version(3)
def test_raise_with_cause():
    check('''
raise e from ee
''')


@only_on_version(3)
def test_Nonlocal():
    check('''
def f(x):
    nonlocal y
''')
    check('''
def f(x):
    nonlocal y, z
''')


@only_on_version(3)
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


@only_on_version(3)
def test_YieldFrom():
    check('yield from x')
    check('1 + (yield from x)')
    check('x = yield from x')
    check('x += yield from x')
    check('return 3, (yield from x)')


@only_on_version(3)
def test_FormattedValue():
    # TODO more
    check('f"a"')


@only_on_version(3)
def test_Bytes():
    check('b"a"')


@only_on_version(3)
def test_NameConstant():
    check('True')


@only_on_version(3)
def test_Starred():
    check('a, *b = 3')
    check('[a, *b]')


@only_on_version(3)
def test_kwonlyargs():
    check('def f(a, *, b=3): pass')
    check('def f(a, *args, b=3): pass')
    check('def f(a, *args, b=3, **kwargs): pass')

