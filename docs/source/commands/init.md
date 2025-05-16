# Init

Init a new course

## Usage

    urnc init [OPTIONS] NAME

## Description

Initializes a new course repository with the following structure:

    <path>
    ├── .git/
    ├── .gitignore
    ├── config.yaml
    └── example.ipynb

## Options

### NAME

The name of the course, e.g. `"My new course"`. Must not contain new lines.

### --help

Show this message and exit.

### -p, --path

The directory path where the course will be created. If not
provided, the path is derived from the course name.

### -u, --url ADMINURL

The git URL for the upstream repository. If a local file path is provided, a
bare repository will be created at that location and configured as the origin
remote.

### --student STUDENTURL

The git URL for the "student" repository, (updated when running `urnc ci`). If a
local file path is provided, a bare repository will be created at that location.
The provided value will be configured as [git.student](../configuration.md#student) in the [config.yaml](../configuration.md).

## Examples

```bash
urnc init "My Example Course"
```
