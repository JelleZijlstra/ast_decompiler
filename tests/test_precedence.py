from .tests import check, only_on_version


def test_Yield() -> None:
    check("def f(): yield")
    check("def f(): x = yield 3")
    check("def f(): return (yield 3)")
    check("def f(): (yield 3)[f] += 4")
    check("def f(): (yield 3)[(yield 4):(yield 5):] += yield 6")
    check("lambda x: (yield x)")
    check("def f(): (yield a), b")


def test_Tuple() -> None:
    check("def f(): return x, y")
    check("def f(): yield x, y")
    check("[(1, 2)]")
    check("{(1, 2): (3, 4)}")
    check("[(a, b) for f in (c, d)]")
    check("(a, b) + 3")
    check("lambda x: (a, b)")
    check("x[(1, 2):(3, 4):(5, 6), (7, 8):]")
    check("()")
    check("x,")


@only_on_version(2)
def test_tuple_in_listcomp() -> None:
    check("[(a, b) for f in c, d]")


@only_on_version(2)
def test_Tuple_arg() -> None:
    check("def f((a, b)): pass")
    check("lambda (a, b): None")


def test_Lambda() -> None:
    check("lambda x: lambda y: x + y")
    check("lambda x: y if z else x")
    check("(lambda x: y) if z else x")
    check("x or (lambda x: x)")
    check("1 + (lambda x: x)")


def test_IfExp() -> None:
    check("y if x else a, b")
    check("(yield y) if (yield x) else (yield a), b")
    check("y if x else z if a else b")
    check("y if x else (z if a else b)")
    check("(y if x else z) if a else b")
    check("y if (x if z else a) else b")
    check("(a and b) if c else d")
    check("a and b if c else d")
    check("a and (b if c else d)")
    check("[x for x in (y if z else x)]")


def test_BinOp() -> None:
    check("(a ** b) ** c")
    check("a ** b ** c")
    check("a ** (b ** c)")
    check("(a + b) * c")
    check("a + b + c")
    check("(a + b) + c")
    check("a + (b + c)")
    check("x * (a or b)")


def test_UnaryOp() -> None:
    check("not not x")
    check("-(not x)")
    check("not (-x)")
    check("(-1) ** x")
    check("-((-1)**x)")


def test_Call() -> None:
    check("f(a, b)")
    check("f((a, b))")
    check("(a, b)(a, b)")
    check("a.b(c, d)")
    check("f((yield a), b)")
    check("f(a, (yield b))")
