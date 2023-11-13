# URNC

Uni Regensburg Notebook Converter

## Installation

```sh
pip install urnc
```

Or update from an older version:

```sh
pip install urnc --upgrade
```

## Usage

```sh
# Clone example course and change into course directory
git clone https://github.com/spang-lab/urnc-example-course
cd urnc-example-course

# Convert a single notebook to student version
urnc convert assignments/sheet1.ipynb student/sheet1.ipynb

# Convert all assignment notebooks to student versions
urnc convert assignments

# Convert all assignment notebooks to student version, pull student repo and
# copy over converted notebooks
urnc student
```

You can find a more detailed introduction to URNC at page [Usage](https://spang-lab.github.io/urnc/getting_started.html) of URNC's [Documentation Website](https://spang-lab.github.io/urnc/).

## Documentation

You can find the full documentation for URNC at [spang-lab.github.io/urnc](https://spang-lab.github.io/urnc/). Amongst others, it includes chapters about:

- [Installation](https://spang-lab.github.io/urnc/installation.html)
- [Usage](https://spang-lab.github.io/urnc/getting_started.html)
- [Configuration](https://spang-lab.github.io/urnc/configuration.html)
- [CLI Reference](https://spang-lab.github.io/urnc/documentation.html)
- [Function Reference](https://spang-lab.github.io/urnc/documentation.html)
- [Contributing](https://spang-lab.github.io/urnc/contributing.html)
- [Testing](https://spang-lab.github.io/urnc/testing.html)
- [Changelog](https://spang-lab.github.io/urnc/changelog.html)
