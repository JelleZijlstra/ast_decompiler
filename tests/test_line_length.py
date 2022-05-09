from .tests import assert_decompiles


def check_split(original: str, multiline: str, length_reduction: int = 2) -> None:
    assert_decompiles(original, original, line_length=len(original))
    assert_decompiles(
        original, multiline, line_length=len(original.strip()) - length_reduction
    )


def test_with_prefix() -> None:
    prefixes = ["from x import"]
    for prefix in prefixes:
        check_split(
            f"{prefix} a, b, c\n",
            f"""{prefix} (
    a,
    b,
    c,
)
""",
        )


def test_del() -> None:
    original = "del a, b, c\n"
    check_split(original, original, length_reduction=10)


def test_import() -> None:
    original = "import a, b, c, d\n"
    check_split(original, original, length_reduction=10)


def test_global() -> None:
    original = "global a, b, c, d\n"
    check_split(original, original, length_reduction=10)


def test_boolop() -> None:
    check_split(
        "if a and b and c:\n    pass\n",
        """if (
    a and
    b and
    c
):
    pass
""",
        length_reduction=12,
    )


def test_display() -> None:
    delimiters = [("{", "}"), ("[", "]"), ("\n\nclass Foo(", "):\n    pass")]
    for start, end in delimiters:
        original = f"{start}a, b, c{end}\n"
        assert_decompiles(original, original, line_length=len(original))

        assert_decompiles(
            original,
            f"""{start}
    a,
    b,
    c,
{end}
""",
            line_length=len(start.lstrip()) + 5,
        )


def test_assign() -> None:
    check_split(
        "a, b, c = lst\n",
        """(
    a,
    b,
    c,
) = lst
""",
        length_reduction=7,
    )

    original = "a = b = c = 3\n"
    check_split(original, original, length_reduction=3)


def test_tuple() -> None:
    check_split(
        "a, b, c\n",
        """(
    a,
    b,
    c,
)
""",
    )


def test_extslice() -> None:
    check_split(
        "d[a:, b, c]\n",
        """d[
    a:,
    b,
    c,
]
""",
    )


def test_comprehension() -> None:
    check_split(
        "[x for y in lst for x in y]\n",
        """[
    x
    for y in lst
    for x in y
]
""",
    )


def test_dict() -> None:
    check_split(
        "{a: b, c: d}\n",
        """{
    a: b,
    c: d,
}
""",
    )


def test_dictcomp() -> None:
    check_split(
        "{a: b for a, b in c}\n",
        """{
    a: b
    for a, b in c
}
""",
    )


def test_function_def() -> None:
    check_split(
        "\ndef f(a, b, *args, **kwargs):\n    pass\n",
        """
def f(
    a,
    b,
    *args,
    **kwargs
):
    pass
""",
        length_reduction=12,
    )


def test_call() -> None:
    check_split(
        "f(a, b, **c)\n",
        """f(
    a,
    b,
    **c
)
""",
    )


def test_nesting() -> None:
    check_split(
        "f(f(a, b, c), g(d, e, f))\n",
        """f(
    f(a, b, c),
    g(d, e, f)
)
""",
        length_reduction=9,
    )
