# Contributing

In case you have **questions**, **feature requests** or find any **bugs** in urnc, please create a corresponding issue at [github.com/spang-lab/urnc/issues](https://github.com/spang-lab/urnc/issues).

In case you want to **write code** for this package, please also create an [Issue](https://github.com/spang-lab/urnc/issues) first, in which you describe your planned code contribution. After acceptance of your proposal by an active maintainer of the repository you will get permissions to create branches for this repository. After this, please follow the steps outlined in [Making Edits](#making-edits) to create a new version of urnc.

## Making Edits

1. Clone the [urnc repository](https://github.com/spang-lab/urnc).
2. Create a new branch for your changes.
3. Make your code changes by updating the files in folder [urnc](https://github.com/spang-lab/urnc/tree/main/urnc).
4. Test your changes by following the steps outlined in [Testing](#testing).
5. If necessary, update the tests in folder [tests](https://github.com/spang-lab/urnc/tree/main/tests).
6. Increase the version in [pyproject.toml](https://github.com/spang-lab/urnc/blob/main/pyproject.toml).
7. Describe your changes in [docs/source/changelog.md](https://github.com/spang-lab/urnc/tree/main/docs/source).
8. Push your changes to the repository.
9. Create a pull request for your changes.
10. Wait for the automated tests to finish.
11. In case the automated tests fail, fix the problems and push the changes to the repository again.
12. In case the automated tests pass, wait for a maintainer to review your changes.
13. After your changes have been accepted, a maintainer will merge your pull request into main and create a new tag.
14. After the tag has been created, a new github release and pypi release will be created automatically.

## Testing

We use [pytest](https://docs.pytest.org/en/latest/) together with [freezegun](https://github.com/spulec/freezegun) and [pytest-cov](https://pypi.org/project/pytest-cov/) for testing. To run the full test suite, install the mentioned packages and `urnc`, then call `pytest` from the root of the repository. The tests are located in the [tests](https://github.com/spang-lab/urnc/tree/main/tests) folder. To run a specific test, use the `-k` flag, e.g., `pytest -k test_version`.

To avoid having to install the package repeatedly after each change, we recommend performing an [editable install](https://setuptools.pypa.io/en/latest/userguide/development_mode.html) using `pip install -e .`. This allows you to modify the source code and run the tests for the modified version without needing to reinstall the package. Note, however, that it is still required to reinstall the package whenever you modify the [`pyproject.toml`](https://github.com/spang-lab/urnc/tree/main/pyproject.toml) file.

See below for a selection of useful commands for testing:

```bash
git clone https://github.com/spang-lab/urnc.git # Clone urnc
cd urnc
pip install -e . # Install urnc in editable mode
pip install pytest pytest-cov freezegun PyYAML # Install testing dependencies
pytest --tb=short # Run tests and show short traceback
pytest -k test_version # Run test_version.py only
pytest -s # Show stdout of commands during tests (useful for debugging)
```

# Documentation

Documentation for this package is generated automatically upon pushes to the `main` branch using [Sphinx](https://www.sphinx-doc.org/en/master/index.html) with the extensions [autodoc](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html) and [myst_parser](https://myst-parser.readthedocs.io/en/latest/). The relevant commands to generate the documentation pages locally are listed below:

```bash
# Install Sphinx and dependencies
pip install sphinx sphinx_rtd_theme myst_parser toml

# Build documentation
cd docs
make html # Other formats are: epub, latex, latexpdf
```
