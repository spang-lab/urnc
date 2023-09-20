# URNC

UR FIDS notebook converter

## Installation

```bash
pip install --upgrade git+https://github.com/spang-lab/urnc.git
```

## Usage

```txt
urnc [-h] [-i EXT] [-f] [-v] [--version] input

Convert Notebooks for UR FIDS Courses

positional arguments:
  input              The input folder, it will be searched recursively

options:
  -h, --help         show this help message and exit
  -i EXT, --ext EXT  The output file extension, use '' for inplace conversion
  -f, --force        Overwrite existing files
  -v, --verbose      Verbose Log output
  --version          show program's version number and exit
```

## Contribution FAQ

### Where to increase the version?

Only in [pyprocject.toml](pyproject.toml).

### When to tag a commit?

Whenever you want the Dockerfile to be rebuilt and pushed. Important: make sure your tag uses the same version as [pyproject.toml](pyproject.toml).
