# Init

Init a new course

## Usage

    urnc init [-p PATH] [-u ADMINURL] [-s STUDENTURL] [-t TEMPLATE] NAME

## Description

Initializes a new course repository with the following structure:

    +------------------------+------------------------------+
    | if TEMPLATE == minimal | if TEMPLATE == full          |
    +------------------------+------------------------------+
    | <path>                 |   <path>                     |
    | ├── .git               |   ├── .git                   |
    | ├── .gitignore         |   ├── .gitignore             |
    | ├── config.yaml        |   ├── config.yaml            |
    | └── example.ipynb      |   ├── images                 |
    |                        |   │   ├── blue_rectangle.png |
    |                        |   │   └── red_circle.png     |
    |                        |   ├── lectures               |
    |                        |   │   └── week1              |
    |                        |   │       ├── lecture1.ipynb |
    |                        |   │       └── lecture2.ipynb |
    |                        |   └── assignments            |
    |                        |       └── week1.ipynb        |
    +------------------------+------------------------------+

## Options

### NAME

The name of the course, e.g. `"My new course"`. Must not contain new lines.

### --help

Show this message and exit.

### -p, --path PATH

The directory path where the course will be created. If not
provided, the path is derived from the course name.

### -u, --url ADMINURL

The git URL for the upstream repository. If a local file path is provided, a
bare repository will be created at that location and configured as the origin
remote.

### -s, --student STUDENTURL

The git URL for the "student" repository, (updated when running `urnc ci`). If a
local file path is provided, a bare repository will be created at that location.
The provided value will be configured as [git.student](../configuration.md#student) in the [config.yaml](../configuration.md).

### -t, --template TEMPLATE

The template to use for the course. Can be "full" or "minimal" (default).

## Examples

```bash
urnc init "My Example Course"
urnc init -t full -p "my_course_2" "My Course 2"
```
