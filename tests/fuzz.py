"""Property-based tests for ast_decompiler, based on those for Black.

By Zac Hatfield-Dodds, based on my Hypothesmith tool for source code
generation.  You can run this file with `python`, `pytest`, or (soon)
a coverage-guided fuzzer I'm working on.
"""

import hypothesmith
from hypothesis import HealthCheck, given, settings

from .tests import check


# This test uses the Hypothesis and Hypothesmith libraries to generate random
# syntatically-valid Python source code and run Black in odd modes.
@settings(
    max_examples=1000,  # roughly 1k tests/minute, or half that under coverage
    derandomize=True,  # deterministic mode to avoid CI flakiness
    deadline=None,  # ignore Hypothesis' health checks; we already know that
    suppress_health_check=HealthCheck.all(),  # this is slow and filter-heavy.
)
@given(
    # Note that while Hypothesmith might generate code unlike that written by
    # humans, it's a general test that should pass for any *valid* source code.
    # (so e.g. running it against code scraped of the internet might also help)
    src_contents=hypothesmith.from_grammar()
    | hypothesmith.from_node()
)
def test_idempotent_any_syntatically_valid_python(src_contents: str) -> None:
    # Before starting, let's confirm that the input string is valid Python:
    compile(src_contents, "<string>", "exec")  # else the bug is in hypothesmith

    check(src_contents)


if __name__ == "__main__":
    # Run tests, including shrinking and reporting any known failures.
    test_idempotent_any_syntatically_valid_python()

    # If Atheris is available, run coverage-guided fuzzing.
    # (if you want only bounded fuzzing, just use `pytest fuzz.py`)
    try:
        import sys
        import atheris
    except ImportError:
        pass
    else:
        test = test_idempotent_any_syntatically_valid_python
        atheris.Setup(sys.argv, test.hypothesis.fuzz_one_input)
        atheris.Fuzz()
