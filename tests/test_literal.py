from tests import assert_decompiles


def test_With():
    assert_decompiles('with x as y, a as b: pass', '''with x as y, a as b:
    pass
''')
    assert_decompiles('''
with x as y:
    with a as b:
        pass
''', '''with x as y, a as b:
    pass
''')


def test_TryFinally():
    assert_decompiles('''
try:
    1 / 0
except Exception as e:
    pass
else:
    print 3
finally:
    print 4
''', '''try:
    1 / 0
except Exception as e:
    pass
else:
    print 3
finally:
    print 4
''')
    assert_decompiles('''
try:
    try:
        1 / 0
    except Exception as e:
        pass
finally:
    print 4
''', '''try:
    1 / 0
except Exception as e:
    pass
finally:
    print 4
''')


def test_If():
    assert_decompiles('''
if x: pass
else:
    if y: pass
    else: pass
''', '''if x:
    pass
elif y:
    pass
else:
    pass
''')
    assert_decompiles('''
if x: pass
elif a:
    if y: pass
    else:
        if z: pass
        else: pass
else:
    pass
''', '''if x:
    pass
elif a:
    if y:
        pass
    elif z:
        pass
    else:
        pass
else:
    pass
''')


def test_BinOp():
    assert_decompiles('''
f(a * b)
''', '''f(a * b)
''')
