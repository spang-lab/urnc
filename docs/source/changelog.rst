Changelog
=========

v1.10.0 (2024-01-04)
-------------------

- Added solution parameter to `urnc.convert.convert`
- Added config option `ci.solution` to `config.yaml`. When specified, `urnc student` now creates student notebooks incl. solution in addition to the usual student notebooks. For details see `https://spang-lab.github.io/urnc/urnc.html#urnc.ci.ci`_.

v1.9.3 (2024-01-01)
-------------------

- Added code coverage calculation to test action
- Test action now also runs regression tests in addition to unit tests.

v1.9.2 (2023-12-19)
-------------------

- Major improvements to unit and regression tests.
- Reverted solution pattern from `^#+ Solution`, `^#+ Skeleton`, `^#+\s*$` to `^###+\s+Solution`, `^###+\s+Skeleton`, `^###+\s*$` to maintain backwards compatibility with existing notebooks (some notebooks in data-science use `# Solution` for already published solutions).

v1.9.0 (2023-12-19)
-------------------

- Added automatic testing upon pull-requests and pushes to main.
- Fixed docstring of `urnc.version.version_self <urnc/version.py>`_.


v1.8.0 (2023-12-19)
-------------------

- Huge refactoring of the code base. All CLI functions are now bundled in one single modules (`urnc/main.py <urnc/main.py>`_).

v1.7.0 (2023-12-18)
-------------------

- Added regression test suite. For details see `docs/source/testing.rst <docs/source/testing.rst>`_.

v1.6.4 (2023-11-13)
-------------------

- Added package documentation in `docs` folder.

v1.5.0
------

- Added the option to provide an `"after"` and `"until"` value for every `git.exclude` config entry. I.e. something like `{pattern: assignments/sheet4.ipynb, after: 2023-12-04}` is now possible.

v1.4.0
------

- Added support for environment variables inside config option `git.student`, i.e. a value like "https://urncbot:{URNC_ACCESS_TOKEN_STUDENT_REPO}@github.com/spang-lab/urnc-example-course-public.git" is now valid.
