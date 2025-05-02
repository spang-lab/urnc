Changelog
=========

v2.0.11 (2025-05-02)
--------------------

- Fixed `student`/ `ci` command. Time zones in timestamps in `config.yaml` are now handled correctly.
- Fixed `urnc covert --solution INPUT`. Manually tagged solutions are no longer removed.

v2.0.10 (2025-04-03)
--------------------

- Fixed solution detection behavior.
- Removed unnecessary `raise` in `urnc pull`.

v2.0.9 (2025-03-21)
-------------------

- Fixed solution detection issues.

v2.0.8 (2025-03-11)
-------------------

- Added log statements for better debugging.

v2.0.7 (2025-03-11)
-------------------

- Added an ignore function to improve flexibility in processing.

v2.0.6 (2025-02-24)
-------------------

- Fixed execution-related issues.

v2.0.5 (2025-02-04)
-------------------

- Fixed issues with the `ci` command.

v2.0.4 (2025-02-03)
-------------------

- Fixed a root key error in configuration handling.

v2.0.3 (2025-02-03)
-------------------

- Added `ipykernel` as a dependency.

v2.0.2 (2025-02-03)
-------------------

- Fixed issues with `strenum`.

v2.0.1 (2025-02-03)
-------------------

- Fixed default branch handling.

v2.0.0 (2024-10-17)
-------------------

- Major changes to `urnc pull` behavior.
- Disabled removal of scroll state in `urnc convert`.
- Added support for subdirectory usage in `urnc ci` and `urnc student`.
- Introduced `config.git.output_dir` for better configuration.

v1.10.6 (2024-09-25)
--------------------

- Fixed regression tests.

v1.10.5 (2024-09-25)
--------------------

- Limited tests to fast tests only.

v1.10.4 (2024-09-25)
--------------------

- Added a pre-release version command.

v1.10.3 (2024-04-11)
--------------------

- Fixed a bug in which student repos could not be pushed by `urnc ci` if the repo already existed on the CI runner machine and was older than the corresponding remote repo (as could occur when using multiple runners which use different drives for caching). Now, whenever the repo already exists a `git pull` is executed before starting the conversion.

v1.10.2 (2024-01-04)
--------------------

- Skeletons are now removed when creating student version with solutions.

v1.10.0 (2024-01-04)
--------------------

- Added solution parameter to `urnc.convert.convert`
- Added config option `ci.solution` to `config.yaml`. When specified, `urnc student` now creates student notebooks incl. solutions in addition to the usual student notebooks. For details see `<https://spang-lab.github.io/urnc/urnc.html#urnc.ci.ci>`_.
- Info messages printed by convert now use relative paths instead of absolute paths to make them more readable.
- Remote images that cannot be verified now cause a warning message instead of an error message.

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
- Added package documentation in `docs` folder.

v1.5.0 (2023-10-16)
------------------

- Added the option to provide an `"after"` and `"until"` value for every `git.exclude` config entry. I.e. something like `{pattern: assignments/sheet4.ipynb, after: 2023-12-04}` is now possible.

v1.4.0 (2023-10-14)
-------------------

- Added support for environment variables inside config option `git.student`, i.e. a value like "https://urncbot:{URNC_ACCESS_TOKEN_STUDENT_REPO}@github.com/spang-lab/urnc-example-course-public.git" is now valid.
- Added a version flag for better version management.
- Moved all print statements to use a logger.

v1.3.0 (2023-10-12)
-------------------

- Added `pull` command

v1.2.0 (2023-10-11)
-------------------

- Changed `ci` command to use a separate "student" repository.

v1.1.0 (2023-10-10)
-------------------

- Added support for skeletons.
- Added a `student` command
- Added a `check` command
- Deprecated the use of "Exercise" in favor of "Assignments".

v1.0.0 (2023-09-22)
-------------------

- Initial stable release.
