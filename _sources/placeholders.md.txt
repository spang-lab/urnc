
# Placeholders

Since most `urnc` commands accept directories as input, it is crucial to have a
flexible mechanism for specifying output paths. Urnc provides this functionality
through a set of placeholder variables, which can be used to define output paths
in commands or configuration files. The supported placeholders are listed
in section [Placeholder Variables](#placeholder-variables).


## Placeholder Variables

- `nb.abspath` Absolute path to the input notebook.
- `nb.absdirpath` Absolute path to the directory containing the notebook.
- `nb.rootpath` Absolute path to the root directory of the notebook.
- `nb.relpath` Relative path to the notebook from the root directory.
- `nb.reldirpath` Relative path to the directory containing the notebook from the root directory.
- `nb.name` Name of the notebook including extension.
- `nb.basename` Name of the notebook without extension.
- `nb.ext` Extension of the notebook without the dot.


## Example

For a input notebook located at
`C:/temp/mycourse/lectures/lecture1.ipynb`, the following placeholders
would be available for constructing the output path:

```python
nb.abspath    = "C:/temp/mycourse/lectures/lecture1.ipynb"
nb.absdirpath = "C:/temp/mycourse/lectures"
nb.rootpath   = "C:/temp/mycourse"
nb.relpath    = "lectures/lecture1.ipynb"
nb.reldirpath = "lectures"
nb.name       = "lecture1.ipynb"
nb.basename   = "lecture1"
nb.ext        = "ipynb"
```


## Motivation

Consider the following course structure::

    C:/temp/mycourse-admin
    ├── config.yaml
    ├── lectures
    │   └── week1
    │       ├── lecture1.ipynb
    │       └── lecture2.ipynb
    └── assignments
        └── week1.ipynb

Now assume we want to create a public version of our course, containing two
versions of each notebook. One version without solutions (for presentation
during the lecture) and one version with solutions (to be released one week
later). Two possible output structures are shown below:

    C:/temp/variant1                       C:/temp/variant2
    ├── lectures                           ├── lectures
    │   └── week1                          │   ├── week1
    │       ├── lecture1.ipynb             │   │   ├── lecture1.ipynb
    │       ├── lecture1-solution.ipynb    │   │   └── lecture2.ipynb
    │       ├── lecture2.ipynb             │   └── week1-solutions
    │       └── lecture2-solution.ipynb    │       ├── lecture1.ipynb
    └── assignments                        │       └── lecture2.ipynb
        └── week1.ipynb                    ├── assignments
        └── week1-solution.ipynb           │   └── week1.ipynb
                                           └── assignments-solutions
                                               └── week1.ipynb

Both of the above structures can be easily generated using the [placeholder
variables](#placeholder-variables) described above. For example, the following
commands would create the above structures:

```bash
# Bash Syntax
out1='C:/temp/variant1/{nb.relpath}'
sol1='C:/temp/variant1/{nb.reldirpath}/{nb.basename}-solution.{nb.ext}'
out2='C:/temp/variant2/{nb.relpath}'
sol2='C:/temp/variant2/{nb.reldirpath}-solutions/{nb.basename}-solution.{n.ext}'
urnc convert --output=$out1 --solution=$sol1 C:/temp/mycourse
urnc convert --output=$out2 --solution=$sol2 C:/temp/mycourse
```

Using [plain directory paths](#plain-directory-paths), the above
commands could be written even shorter, as:

```bash
out1='C:/temp/variant1'
sol1='C:/temp/variant1'
out2='C:/temp/variant2'
sol2='C:/temp/variant2/{nb.reldirpath}-solutions/{nb.basename}-solution.{n.ext}'
urnc convert --output=$out1 --solution=$sol1 C:/temp/mycourse
urnc convert --output=$out2 --solution=$sol2 C:/temp/mycourse
```


## Plain Directory Paths

To make specifying output paths less verbose, urnc also accepts "plain directory
paths" as output paths. A path is considered a plain directory path if it does
neither end with `.ipynb` nor contain any placeholders. If a plain directory
path is provided, the notebooks will be stored inside that directory in the same
subfolder they had in the original input directory. However, to avoid
overwriting outputs of previous targets, each target will use a different file
name for the notebooks in this case. The following rules apply:

| Target     | Naming Pattern                                    |
| ---------- | ------------------------------------------------- |
| `student`  | `{nb.reldirpath}/{nb.basename}.{nb.ext}`          |
| `solution` | `{nb.reldirpath}/{nb.basename}-solution.{nb.ext}` |
| `execute`  | `{nb.reldirpath}/{nb.basename}-executed.{nb.ext}` |
| `clear`    | `{nb.reldirpath}/{nb.basename}-cleared.{nb.ext}`  |
| `fix`      | `{nb.reldirpath}/{nb.basename}-fixed.{nb.ext}`    |


## Limitations

The placeholder variables `nb.rootpath`, `nb.relpath` and `nb.reldirpath`
require the "root" [^1] of the current course to be specified. Usually, this is
done by searching the file system upwards from the given input path, until a
`config.yaml` file is found. If no `config.yaml` file is found, the current
working directory is considered the course root. This scenario could happen,
e.g., if `urnc convert` is used on a single notebook outside a specific course.

[^1]: Sometimes, the "course root" is also referred to as "course base", "course
    base directory" or "course basepath".