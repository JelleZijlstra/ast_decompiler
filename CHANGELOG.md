version 0.8.0 (May 17, 2024)
- Support Python 3.12 and 3.13; stop testing Python 3.6 and 3.7
- Fix all DeprecationWarnings in the codebase

version 0.7.0 (October 3, 2022)
- Stop adding redundant parentheses to `complex` numbers with no real part and a negative
  imaginary part (thanks to Alex Waygood)

version 0.6.0 (June 6, 2022)
- Support Python 3.11
- Fix bug where annotations on `*args` and `**kwargs` were dropped
- Stop adding redundant parentheses to tuple subscripts on Python 3.8 and lower
  (thanks to Alex Waygood)

version 0.5.0 (May 10, 2022)
- Add `py.typed`
- Fix decompilation of f-strings containing escaped braces
- Preserve literal newlines in docstrings
- Fix decompilation of complex infinity
- Add support for Python 3.10 pattern matching
- Fix incorrect decompilation of lambdas in comprehension guards on Python 3.9 and higher
- Fix decompilation for dict `**` unpacking
- Modernize CI and packaging setup
- Fix tests under Python 3.9
- Add explicit LICENSE file

version 0.4.0 (May 7, 2020)
- Support Python 3.7 and 3.8 (thanks to Luke Plant)
- Allow keyword-only arguments without default values (thanks to Shantanu Jain)

version 0.3.2 (August 22, 2017)
- More f-string fixes (thanks to Shantanu Jain)

version 0.3.1 (August 11, 2017)
- Fix handling of f-strings

version 0.3 (January 7, 2017)
- Support Python 3.6

version 0.2 (July 14, 2016)
- Support Python 3

version 0.1 (May 7, 2016)
- Initial version
