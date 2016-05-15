from tests import assert_decompiles


def test_indentation():
    assert_decompiles('''
if x:
    pass
''', '''if x:
 pass
''', indentation=1)


def test_with_prefix():
    prefixes = [
        'from x import',
        'import',
        'del',
        'global',
    ]
    for prefix in prefixes:
        original = "%s a, b, c\n" % prefix
        assert_decompiles(original, original, line_length=len(original))

        assert_decompiles(original, '''%s (
    a,
    b,
    c,
)
''' % prefix, line_length=len(original.strip()) - 2)


def test_boolop():
    original = 'if a and b and c:\n    pass\n'
    assert_decompiles(original, original, line_length=len(original))

    assert_decompiles(original, '''if (
    a and
    b and
    c
):
    pass
''', line_length=8)


def test_display():
    delimiters = [
        ('{', '}'),
        ('[', ']'),
        ('f(', ')'),
        ('\n\nclass Foo(', '):\n    pass')
    ]
    for start, end in delimiters:
        original = '%sa, b, c%s\n' % (start, end)
        assert_decompiles(original, original, line_length=len(original))

        assert_decompiles(original, '''%s
    a,
    b,
    c,
%s
''' % (start, end), line_length=len(start.lstrip()) + 5)


def test_assign():
    original = 'a, b, c = lst\n'
    assert_decompiles(original, original, line_length=len(original))

    assert_decompiles(original, '''(
    a,
    b,
    c,
) = lst
''', line_length=6)


def test_tuple():
    original = 'a, b, c\n'
    assert_decompiles(original, original, line_length=len(original))

    assert_decompiles(original, '''(
    a,
    b,
    c,
)
''', line_length=6)


def test_extslice():
    original = 'd[a:, b, c]\n'
    assert_decompiles(original, original, line_length=len(original))

    assert_decompiles(original, '''d[
    a:,
    b,
    c,
]
''', line_length=6)


def test_comprehension():
    original = '[x for y in lst for x in y]\n'
    assert_decompiles(original, original, line_length=len(original))
    assert_decompiles(original, '''[
    x
    for y in lst
    for x in y
]
''', line_length=len(original.strip()) - 2)
