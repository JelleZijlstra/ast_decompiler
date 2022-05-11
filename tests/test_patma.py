from .tests import check, skip_before


@skip_before((3, 10))
def test_patma() -> None:
    check(
        """
match x:
    case y | z:
        pass
    case a(b, c, z=3) if whatever:
        pass
    case [1, 2, 3] if y if x else z:
        pass
    case [1, 2, 3, *_]:
        pass
    case [1, 2, 3, *rest]:
        pass
    case {"x": y, "z": 3}:
        pass
    case y:
        pass
    case 3:
        pass
    case -1:
        pass
    case _:
        pass
"""
    )


@skip_before((3, 10))
def test_precedence() -> None:
    check(
        """
match x:
    case (y | z) as a:
        pass
    case y | (z as a):
        pass
    case (y as z) as a:
        pass
    case y | z as a:
        pass
    case y | (z | a):
        pass
    case (y | z) | a:
        pass
"""
    )
