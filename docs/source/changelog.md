# Changelog

## v2.1.1 (2025-05-16)

- Added descriptions to previously undocumented CLI options.
- Improved existing descriptions of CLI options.

## v2.1.0 (2025-05-16)

API Related:

- Added documentation for 'Existing commands', 'Configuration options' and
  'Placeholders'
- Improved documentation for 'Contributing' and 'Changelog'
- Removed documentation for 'Modules' (The python interface is considered
  internal and therefore only the command line interface will be documented in
  future versions)
- Added the following new arguments to `urnc init`:
  - `-p, --path DIRECTORY`: Output directory
  - `-u, --url TEXT`: Git URL for admin repository
  - `-s, --student TEXT`: Git URL for student repository

Internal:

- Added tests for MacOS and Windows
- Added tests for python versions 3.9, 3.10, 3.11 and 3.13
- Fixed coverage upload in CI
- Switched docs to Markdown format
- Added type hints to almost every function
- Added dev dependencies to pyproject.toml, i.e.,
  urnc can now be installed with `pip install urnc[dev]` to get all
  development dependencies as well.
- Added `pyrightconfig.json` and recommended pyright as type checker in the
  contribution guidelines.
- Added tests for `convert` and `merge_dict`
- Added `url` and `student_url` arguments to `urnc.pull.pull`
- Made lots of refactorings to support python version below 3.12, e.g.:
  - Used `if/else` instead of `match` (Python 3.10+)
  - Used `Enum` instead of `StrEnum` (Python 3.11+)
- Made even more refactorings to fix type check findings
- Added temp folders to `.gitignore`
- Simplified `test_ci.py`

## v2.0.12 (2025-05-07)

- Fixed a bug where multiple targets were falsely generated in sequence. For example, if both 'student' and 'solution' targets were defined, the solution target was created from the 'student' version after solutions had already been removed.

## v2.0.11 (2025-05-02)

- Fixed `student`/ `ci` command: time zones in timestamps in `config.yaml` are now handled correctly.
- Fixed `urnc convert --solution INPUT`: manually tagged solutions are no longer removed.

## v2.0.10 (2025-04-03)

- Fixed solution detection behavior.
- Removed unnecessary `raise` in `urnc pull`.

## v2.0.9 (2025-03-21)

- Fixed solution detection issues.

## v2.0.8 (2025-03-11)

- Added log statements for better debugging.

## v2.0.7 (2025-03-11)

- Added an ignore function to improve flexibility in processing.

## v2.0.6 (2025-02-24)

- Fixed execution-related issues.

## v2.0.5 (2025-02-04)

- Fixed issues with the `ci` command.

## v2.0.4 (2025-02-03)

- Fixed a root key error in configuration handling.

## v2.0.3 (2025-02-03)

- Added `ipykernel` as a dependency.

## v2.0.2 (2025-02-03)

- Fixed issues with `strenum`.

## v2.0.1 (2025-02-03)

- Fixed default branch handling.

## v2.0.0 (2024-10-17)

- Major changes to `urnc pull` behavior.
- Disabled removal of scroll state in `urnc convert`.
- Added support for subdirectory usage in `urnc ci` and `urnc student`.
- Introduced `config.git.output_dir` for better configuration.

## v1.10.6 (2024-09-25)

- Fixed regression tests.

## v1.10.5 (2024-09-25)

- Limited tests to fast tests only.

## v1.10.4 (2024-09-25)

- Added a pre-release version command.

## v1.10.3 (2024-04-11)

- Fixed a bug in which student repos could not be pushed by `urnc ci` if the repo already existed on the CI runner machine and was older than the corresponding remote repo (as could occur when using multiple runners which use different drives for caching). Now, whenever the repo already exists a `git pull` is executed before starting the conversion.

## v1.10.2 (2024-01-04)

- Skeletons are now removed when creating student version with solutions.

## v1.10.0 (2024-01-04)

- Added solution parameter to `urnc.convert.convert`
- Added config option `ci.solution` to `config.yaml`. When specified, `urnc student` now creates student notebooks including solutions in addition to the usual student notebooks.
- Info messages printed by convert now use relative paths instead of absolute paths to make them more readable.
- Remote images that cannot be verified now cause a warning message instead of an error message.

## v1.9.3 (2024-01-01)

- Added code coverage calculation to test action
- Test action now also runs regression tests in addition to unit tests.

## v1.9.2 (2023-12-19)

- Improved unit and regression tests for better reliability.
- Reverted solution pattern to maintain compatibility with older notebooks. This ensures that existing notebooks using "# Solution" will still work as expected.

## v1.9.0 (2023-12-19)

- Added automatic testing for pull requests and pushes to the main branch. This helps ensure code quality and stability.
- Fixed a minor issue in the versioning function's documentation.

## v1.8.0 (2023-12-19)

- Refactored the codebase significantly. All command-line interface (CLI) functions are now organized in a single module, making the code easier to maintain and extend.

## v1.7.0 (2023-12-18)

- Introduced a regression test suite to ensure new changes do not break existing functionality. Details are available in the `testing` documentation.
- Added comprehensive package documentation in the `docs` folder.

## v1.5.0 (2023-10-16)

- Added support for specifying "after" and "until" values in the `git.exclude` configuration. This allows users to exclude files based on specific time ranges, such as `{pattern: assignments/sheet4.ipynb, after: 2023-12-04}`.

## v1.4.0 (2023-10-14)

- Added support for environment variables in the `git.student` configuration. For example, you can now use a value like `https://urncbot:{URNC_ACCESS_TOKEN_STUDENT_REPO}@github.com/spang-lab/urnc-example-course-public.git`.
- Introduced a version flag for better version management.
- Replaced print statements with a logging system for improved debugging and output control.

## v1.3.0 (2023-10-12)

- Introduced the `pull` command to fetch updates from remote repositories.

## v1.2.0 (2023-10-11)

- Updated the `ci` command to use a separate "student" repository for better organization and workflow.

## v1.1.0 (2023-10-10)

- Added support for skeletons, allowing users to create templates for assignments.
- Introduced the `student` command to generate student versions of notebooks.
- Added the `check` command to validate notebooks for errors.
- Deprecated the use of "Exercise" in favor of "Assignments" for better clarity.

## v1.0.0 (2023-09-22)

- Initial stable release of the URNC tool.
