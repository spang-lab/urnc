# Contributing

## Always start with an Issue

In case you have **questions**, **feature requests** or find any
**bugs** in urnc, please create a corresponding [issue].

In case you want to **write code** for this package, please also
create an issue first, in which you describe your planned code
contribution. After acceptance of your proposal by an active
maintainer of the repository you will get permissions to create
branches for this repository. After this, follow the steps
outlined below to create a new version of urnc.

## Making Updates

1. **Clone**
    - Clone the [urnc repository]
    - Create a new branch for your changes
2. **Edit, Test and Document**
    - Update the files in folder [urnc]
    - Use [autopep8] to format your code
    - Use [pyright] for type checking
    - Test your changes as described in [Testing]
    - If necessary, add or update the [tests]
    - Increase the version in [pyproject.toml]
    - Describe your changes in [docs/source/changelog.md]
3. **Push and create a Pull Request**
    - Push your changes
    - Create a pull request
    - Wait for the automated tests to finish
    - If any test fails, fix and repeat
    - If all tests pass, wait for a maintainer to review your changes
4. **Wait for acceptance**
    - If a maintainer requests changes, make the changes and push again
    - If a maintainer approves your changes, they will merge your pull request into main and create a new version tag
    - After the tag has been created, a new github release and pypi release will be created automatically.

[issue]: https://github.com/spang-lab/urnc/issues
[urnc repository]: https://github.com/spang-lab/urnc
[urnc]: https://github.com/spang-lab/urnc/tree/main/urnc
[tests]: https://github.com/spang-lab/urnc/tree/main/tests
[pyproject.toml]: https://github.com/spang-lab/urnc/blob/main/pyproject.toml
[Testing]: #testing
[docs/source/changelog.md]: https://github.com/spang-lab/urnc/tree/main/docs/source
[pyright]: https://microsoft.github.io/pyright/#/
[autopep8]: https://pypi.org/project/autopep8/

## Testing

We use [pytest](https://docs.pytest.org/en/latest/) together with [freezegun](https://github.com/spulec/freezegun) and [pytest-cov](https://pypi.org/project/pytest-cov/) for testing. To run the full test suite, install the mentioned packages and `urnc`, then call `pytest` from the root of the repository. The tests are located in the [tests](https://github.com/spang-lab/urnc/tree/main/tests) folder. To run a specific test, use the `-k` flag, e.g., `pytest -k test_version`.

To avoid having to install the package repeatedly after each change, we recommend performing an [editable install](https://setuptools.pypa.io/en/latest/userguide/development_mode.html) using `pip install -e .`. This allows you to modify the source code and run the tests for the modified version without needing to reinstall the package. Note, however, that it is still required to reinstall the package whenever you modify the [`pyproject.toml`](https://github.com/spang-lab/urnc/tree/main/pyproject.toml) file.

See below for a selection of useful commands for testing:

```bash
# Install urnc in editable mode (incl. dev dependencies)
git clone https://github.com/spang-lab/urnc.git
cd urnc
pip install -e .[dev]

# Run tests
pytest                 # Run all tests
pytest -k test_version # Run only tests from test_version.py
pytest -s              # Show STDOUT during tests
pytest -n 2            # Use 2 cores (requires pytest-xdist)
```

Hint: if you're not using your system's default python version, you may need to use `python -m pytest` instead of `pytest` in the commands above.

## Documentation

Documentation for this package is generated automatically upon pushes to the `main` branch using [Sphinx](https://www.sphinx-doc.org/en/master/index.html) with the extensions [autodoc](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html) and [myst_parser](https://myst-parser.readthedocs.io/en/latest/). The relevant commands to generate the documentation pages locally are listed below:

```bash
# Install urnc in editable mode (incl. dev dependencies)
git clone https://github.com/spang-lab/urnc.git
cd urnc
pip install -e .[dev]

# Build documentation
cd docs
make html # Other formats are: epub, latex, latexpdf
```
