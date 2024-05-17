from .tests import check, skip_before


@skip_before((3, 12))
def test_generic_class() -> None:
    check(
        """
class C[T: int, *Ts, **P]:
    pass
"""
    )


@skip_before((3, 12))
def test_generic_function() -> None:
    check(
        """
def f[T: int, *Ts, **P](a: T, b: Ts, c: P) -> None:
    pass
"""
    )


@skip_before((3, 12))
def test_type_alias() -> None:
    check(
        """
type X = int
type Y[T: (int, str), *Ts, *P] = T
"""
    )
