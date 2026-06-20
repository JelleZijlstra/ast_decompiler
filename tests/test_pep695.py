import ast

from ast_decompiler import decompile

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


@skip_before((3, 12))
def test_multiline_type_params() -> None:
    source = """
def f[LongName: int, *LongTuple, **LongParams]() -> None:
    pass

class C[LongName: int, *LongTuple, **LongParams]:
    pass

type Alias[LongName: int, *LongTuple, **LongParams] = LongName
"""
    decompiled = decompile(ast.parse(source), line_length=20)

    ast.parse(decompiled)


@skip_before((3, 13))
def test_type_var_default() -> None:
    check(
        """
def f[T=int, *Ts=(int, str), **P=()]() -> None:
    pass
"""
    )
