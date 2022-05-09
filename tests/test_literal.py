from .tests import assert_decompiles, only_on_version


def test_With() -> None:
    assert_decompiles(
        "with x as y, a as b: pass",
        """with x as y, a as b:
    pass
""",
    )


@only_on_version(2)
def test_With_collapsed() -> None:
    assert_decompiles(
        """
with x as y:
    with a as b:
        pass
""",
        """with x as y, a as b:
    pass
""",
    )


def test_TryFinally() -> None:
    assert_decompiles(
        """
try:
    1 / 0
except Exception as e:
    pass
else:
    z = 3
finally:
    z = 4
""",
        """try:
    1 / 0
except Exception as e:
    pass
else:
    z = 3
finally:
    z = 4
""",
    )


@only_on_version(2)
def test_TryFinally_collapsed() -> None:
    assert_decompiles(
        """
try:
    try:
        1 / 0
    except Exception as e:
        pass
finally:
    z = 4
""",
        """try:
    1 / 0
except Exception as e:
    pass
finally:
    z = 4
""",
    )


def test_If() -> None:
    assert_decompiles(
        """
if x: pass
else:
    if y: pass
    else: pass
""",
        """if x:
    pass
elif y:
    pass
else:
    pass
""",
    )
    assert_decompiles(
        """
if x: pass
elif a:
    if y: pass
    else:
        if z: pass
        else: pass
else:
    pass
""",
        """if x:
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
""",
    )


def test_BinOp() -> None:
    assert_decompiles(
        """
f(a * b)
""",
        """f(a * b)
""",
    )
