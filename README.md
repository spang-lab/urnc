# URNC

UR FIDS notebook converter

## Installation

```sh
pip install urnc
```

Or update from an older version:

```sh
pip install urnc --upgrade
```

## Usage for a course

All following commands assume your working directory is somewhere inside a course directory:

```sh
cd my_urnc_course
```

Check the current course version:

```sh
urnc version
```

Edit the course files.

Check for errors only:

```sh
urnc check .
```

See how the course will look for a student by converting your notebook files:

```sh
urnc convert . ./student
```

This will create a copy of all notebook files in the folder `student` and convert them to the student version.
You can check the output with jupyter, e.g:

```sh
cd student
jupyter-lab
```

Once you are happy with your changes commit them. Make sure to delete the `student` folder again or add it to `.gitignore`. In the clean repo use urnc to create a version commit:

```sh
urnc version patch
git push --follow-tags
```

The `--follow-tags` option is only required if git does not push tags by default. We recommend configuring git to push tags automatically:

```sh
git config --global push.followTags true
```

The version is a [semver](https://semver.org). You can also run:

```sh
urnc version minor
urnc version major
```

This will trigger the ci pipeline of the repo and create a student branch.

## Contribution

First check that you have the latest version of this repo:

```sh
git pull
urnc version --self
```

If you want to make changes to `urnc` update the python files in `urnc` and test your changes as described in section [Testing](#testing). When you are happy with your changes, push them to Github. Afterwards use the following commands to create a tagged commit and trigger the Github actions:

```sh
urnc version --self patch
# or urnc version --self minor
# or urnc version --self major
git push --follow-tags
```

The `--follow-tags` option is only required if git does not push tags by default. We recommend configuring git to push tags automatically:

```sh
git config --global push.followTags true
```

## Testing

The easiest way to test [urnc](https://github.com/spang-lab/urnc) updates on real data is to:

1. Clone urnc
2. Clone your course of interest, e.g. [urnc-example-course](https://github.com/spang-lab/urnc-example-course)
3. Add the folder you cloned `urnc` into to your `PYTHONPATH`
4. Call urnc as usual

The corresponding commands are something like:

```bash
# Clone urnc and urnc-example-course
git clone https://github.com/spang-lab/urnc.git
git clone https://github.com/spang-lab/urnc-example-course.git

# Add urnc to your pythonpath
export "PYTHONPATH=$(pwd)/urnc" # bash/zsh syntax
$env:PYTHONPATH = "$(pwd)\urnc" # powershell syntax

# Make some updates to ./urnc/urnc/*.py

# Call urnc as usual
pushd urnc-example-course
urnc student
popd
```

## Documentation

Documentation for this package is generated automatically upon pushes to main using [sphinx](https://www.sphinx-doc.org/en/master/index.html) with extensions [autodoc](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html) and [myst_parser](https://myst-parser.readthedocs.io/en/latest/). The relevant commands to generate the documentation pages locally, are listed in the following:

```bash
# Install sphinx and myst-parser (for markdown support)
pip install sphinx myst-parser sphinx_rtd_theme

# Create rst files from urnc docstrings
sphinx-apidoc -o docs urnc

# Build documentation
cd docs
make html # other formats are: epub, latex, latexpdf
sphinx-build -M html source build # this is what make does
```

## Changelog

- `v1.5.0`: Added the option to provide an `"after"` and `"until"` value for every `git.exclude` config entry. I.e. something like `{pattern: assignments/sheet4.ipynb, after: 2023-12-04}` is now possible.
- `v1.4.0`: Added support for environment variables inside config option `git.student`, i.e. a value like "https://urncbot:{URNC_ACCESS_TOKEN_STUDENT_REPO}@github.com/spang-lab/urnc-example-course-public.git" is now valid.