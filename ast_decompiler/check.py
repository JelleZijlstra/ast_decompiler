import ast
from ast_decompiler import decompile
import difflib


def check(code: str) -> None:
    """Checks that the code remains the same when decompiled and re-parsed."""
    tree = ast.parse(code)
    new_code = decompile(tree)
    try:
        new_tree = ast.parse(new_code)
    except SyntaxError as e:
        if e.lineno is None:
            raise
        print(">>> syntax error:")
        lineno = e.lineno - 1
        min_lineno = max(0, lineno - 3)
        max_lineno = lineno + 3
        for line in new_code.splitlines()[min_lineno:max_lineno]:
            print(line)
        raise

    dumped = ast.dump(ast.parse(code))
    new_dumped = ast.dump(new_tree)

    if dumped != new_dumped:
        print(code)
        print(new_code)
        for line in difflib.unified_diff(dumped.split(), new_dumped.split()):
            print(line)
        assert False, f"{dumped} != {new_dumped}"
