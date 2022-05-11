"""

Helpers for tests.

"""

import ast
from typing import Any, Tuple, Callable, TypeVar
from ast_decompiler import decompile
from ast_decompiler.check import check as check
import difflib
import sys

VERSION = sys.version_info.major

_CallableT = TypeVar("_CallableT", bound=Callable[..., None])


def assert_decompiles(
    code: str,
    result: str,
    do_check: bool = True,
    indentation: int = 4,
    line_length: int = 100,
    starting_indentation: int = 0,
) -> None:
    """Asserts that code, when parsed, decompiles into result."""
    decompile_result = decompile(
        ast.parse(code),
        indentation=indentation,
        line_length=line_length,
        starting_indentation=starting_indentation,
    )
    if do_check:
        check(decompile_result)
    if result != decompile_result:
        print(">>> expected")
        print(result)
        print(">>> actual")
        print(decompile_result)
        print(">>> diff")
        for line in difflib.unified_diff(
            result.splitlines(), decompile_result.splitlines()
        ):
            print(line)
        assert False, f"failed to decompile {code}"


def only_on_version(py_version: int) -> Callable[[_CallableT], _CallableT]:
    """Decorator that runs a test only if the Python version matches."""
    if py_version != VERSION:

        def decorator(fn: Callable[..., Any]) -> Callable[..., None]:
            return lambda *args: None

    else:

        def decorator(fn: _CallableT) -> _CallableT:
            return fn

    return decorator


def skip_before(py_version: Tuple[int, int]) -> Callable[[_CallableT], _CallableT]:
    """Decorator that skips a test on Python versions before py_version."""
    if sys.version_info < py_version:

        def decorator(fn: Callable[..., Any]) -> Callable[..., None]:
            return lambda *args: None

    else:

        def decorator(fn: _CallableT) -> _CallableT:
            return fn

    return decorator


def skip_after(py_version: Tuple[int, int]) -> Callable[[_CallableT], _CallableT]:
    """Decorator that skips a test on Python versions after py_version."""
    if sys.version_info > py_version:

        def decorator(fn: Callable[..., Any]) -> Callable[..., None]:
            return lambda *args, **kwargs: None

    else:

        def decorator(fn: _CallableT) -> _CallableT:
            return fn

    return decorator
