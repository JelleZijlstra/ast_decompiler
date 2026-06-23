import ast

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


@skip_before((3, 10))
def test_multiline_match_or() -> None:
    check(
        """
match x:
    case b"aaaaaaaaaaaaaaaaaaaaaaaa" | "bbbbbbbbbbbbbbbbbbbbbbbb":
        pass
    case a(y=(b"aaaaaaaaaaaaaaaaaaaaaaaa" | "bbbbbbbbbbbbbbbbbbbbbbbb")):
        pass
""",
        line_length=40,
    )


@skip_before((3, 10))
def test_multiline_match_mapping_with_rest() -> None:
    check(
        """
match x:
    case {
        b"aaaaaaaaaaaaaaaaaaaaaaaa": first,
        b"bbbbbbbbbbbbbbbbbbbbbbbb": second,
        **rest,
    }:
        pass
""",
        line_length=40,
    )
