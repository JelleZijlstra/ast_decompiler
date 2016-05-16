from tests import check


def test_FunctionDef():
    check('''
@foo
def bar(x):
    pass
''')
    check('def foo(): pass')
    check('def foo(a): pass')
    check('def foo(a, b): pass')
    check('def foo(a, b=3): pass')
    check('def foo(a, b, *args): pass')
    check('def foo(a, b, *args, **kwargs): pass')
    check('def foo(a, b=3, **kwargs): pass')


def test_ClassDef():
    check('''
@foo
class Bar(object):
    pass
''')
    check('class Bar: pass')
    check('class Bar(object): pass')
    check('class Bar(int, str): pass')


def test_Return():
    check('def foo(): return')
    check('def foo(): return 3')


def test_Delete():
    check('del a')
    check('del a, b')
    check('del a, b[c]')


def test_Assign():
    check('x = 3')
    check('x = y = 3')


def test_AugAssign():
    check('x += 3')
    check('y *= 5')


def test_Print():
    check('print')
    check('print >>sys.stderr')
    check('print a, b')
    check('print a, b,')
    check('print a,')
    check('print >>sys.stderr, a, b,')


def test_For():
    check('for x in y: pass')
    check('''
for x in y:
    pass
else:
    print 3
''')


def test_While():
    check('while foo: pass')
    check('''
while foo:
    break
else:
    3
''')


def test_If():
    check('if x: pass')
    check('''
if x:
    pass
else:
    pass
''')
    check('''
if x:
    pass
elif y:
    pass
else:
    pass
''')

def test_With():
    check('with x: pass')
    check('with x as y: pass')
    check('with x as y, a as b: pass')
    check('with x as y, a: pass')
    check('''
with x as y:
    with a as b:
        with c as d:
            pass
''')


def test_Raise():
    check('raise')
    check('raise e')
    check('raise TypeError, e')
    check('raise TypeError, e, tb')


def test_TryExcept():
    check('''
try:
    1/0
except:
    pass
else:
    pass
''')
    check('''
try:
    1/0
except:
    pass
''')
    check('''
try:
    1/0
except Exception:
    pass
''')
    check('''
try:
    1/0
except Exception as e:
    pass
''')
    check('''
try:
    1/0
except (Exception, KeyboardInterrupt):
    pass
''')


def test_TryFinally():
    check('''
try:
    1/0
finally:
    leave()
''')


def test_Assert():
    check('assert False')
    check('assert False, "hello"')


def test_Import():
    check('import x')
    check('import x as y')
    check('import x, y')
    check('import x as y, z')


def test_ImportFrom():
    check('from . import foo')
    check('from .foo import bar')
    check('from foo import bar')
    check('from ....... import bar as foo')


def test_Exec():
    check('exec "hello"')
    check('exec "hello" in {}')
    check('exec "hello" in {}, {}')


def test_Global():
    check('global a')
    check('global a, b')


def test_Expr():
    check('call()')


def test_Pass():
    check('pass')


def test_Break():
    check('while True: break')


def test_Continue():
    check('while True: continue')


def test_BoolOp():
    check('x and y')
    check('x and y and z')
    check('x or y')
    check('x or y or z')
    check('x and (y or z)')
    check('(x and y) or z')


def test_Binop():
    check('x + y')
    check('x / y')
    check('x in y')


def test_UnaryOp():
    check('not x')
    check('+x')


def test_Lambda():
    check('lambda: None')
    check('lambda x: None')
    check('lambda x: x ** x')


def test_IfExp():
    check('x if y else z')


def test_Dict():
    check('{}')
    check('{1: 2}')
    check('{1: 2, 3: 4}')


def test_Set():
    check('{1}')
    check('{1, 2}')


def test_ListComp():
    check('[x for x in y]')
    check('[x for x in y if z]')
    check('[x for x in y for z in a]')


def test_SetComp():
    check('{x for x in y}')
    check('{x for x in y if z}')
    check('{x for x in y for z in a}')


def test_DictComp():
    check('{x: y for x in y}')
    check('{x: z for x in y if z}')
    check('{x: a for x in y for z in a}')


def test_GeneratorExp():
    check('(x for x in y)')
    check('(x for x in y if z)')
    check('(x for x in y for z in a)')


def test_Yield():
    check('def f(): yield')
    check('def f(): yield 3')
    check('def f(): x = yield 3')
    check('def f(): print (yield 4)')


def test_Compare():
    check('x < y')
    check('x > y < z')
    check('x == y > z')


def test_Call():
    check('f()')
    check('f(1)')
    check('f(1, x=2)')
    check('f(*args, **kwargs)')
    check('f(foo, *args, **kwargs)')


def test_Repr():
    check('`foo`')


def test_Num():
    check('1')
    check('1.0')
    check('1.0e10')
    check('1+2j')


def test_Str():
    check('"foo"')
    check('u"foo"')
    check('"foo\\"bar"')
    check('''from __future__ import unicode_literals
b'foo'
''')


def test_Attribute():
    check('a.b')


def test_Subscript():
    check('x[y]')


def test_Name():
    check('x')


def test_List():
    check('[]')
    check('[a]')
    check('[a, b]')


def test_Tuple():
    check('()')
    check('(a,)')
    check('(a, b)')


def test_Slice():
    check('x[:]')
    check('x[1:]')
    check('x[:1]')
    check('x[1::-1]')


def test_ExtSlice():
    check('x[:, :]')
    check('x[1:, :1]')


def test_files():
    with open('ast_decompiler/decompiler.py') as f:
        code = f.read()
    check(code)
