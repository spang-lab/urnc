# convert

Converts INPUT notebooks to the specified TARGET formats and writes them to OUTPUT.


## Usage

    urnc convert [-f|-n|-i] [-t TARGET] [-s SOLUTION] [-o OUTPUT] INPUT


## Description

Notebook conversion by `urnc` happens in two stages:

1. All lines of INPUT notebooks are checked for [keywords].
   If a keyword is found, the containing cell is [tagged] accordingly.
2. All tagged cells are processed according to the specified TARGET format.

This two-stage approach allows manual tagging of cells in addition to the
use of keywords to configure the conversion behaviour. See [TARGET](#target) for
a description of the effect of each tag on the conversion targets.


## Options


### INPUT

Path to a single input notebook or a directory containing notebooks.
If INPUT is a directory, all notebooks in the directory are converted recursively.


### -t, --target TARGET

Specifies the conversion target(s), i.e., the type of conversion(s) to be
performed. Can be a comma-separated list of multiple conversion targets. If no
TARGET is specified, `student` is used by default (i.e., a notebook for
"students" is produced). Valid targets are: `student`, `solution`, `execute`,
`clear`, and `fix`. Depending on the target(s), the following actions are
performed for each INPUT notebook:

1. `student`:
    1. Tag cells matching `## <solution-keyword>` as `solution`.
    2. Tag cells matching `## <skeleton-keyword>` as `skeleton`.
    3. Find cells tagged as `solution` and/or `skeleton` but not as `ignore`.
    4. Remove `solution` lines and uncomment `skeleton` lines from these cells.

2. `solution`:
    1. Tag cells matching `## <skeleton-keyword>` as `skeleton`.
    2. Find cells tagged as `skeleton`, but not as `ignore`.
    3. Uncomment `skeleton` lines in these cells.

3. `execute`:
    1. Tag cells matching `## <solution-keyword>` as `solution`.
    2. Find cells tagged as `solution` but not as `noexecute`.
    3. Execute these cells.

4. `clear`:
    1. Clear all output cells in the notebook.

5. `fix`:
    1. Fix all image paths in the notebook.

A summary of the effect of each tag (rows) on each target (columns) is shown below:

|                 | student   | solution | execute | clear | fix |
| --------------- | --------- | -------- | ------- | ----- | --- |
| ignore          | skip      | skip     | .       | .     | .   |
| noexecute       | .         | .        | skip    | .     | .   |
| solution        | remove    | .        | execute | .     | .   |
| skeleton        | uncomment | remove   | .       | .     | .   |
| assignment      | .         | .        | .       | .     | .   |
| assignmentstart | .         | .        | .       | .     | .   |


### -o, --output OUTPUT

Path for storing the converted notebook(s).
Can be a file or directory path.
If no OUTPUT is specified, `out/` is used by default.
Supports [placeholder variables].
If TARGET is given as a comma-separated list of multiple targets, OUTPUT can be specified as a comma-separated list of the same length.


### -s, --solution SOLUTION

**DEPRECATED**: Use `-t solution -o SOLUTION` instead.

Path for storing the output of the `solution` target.
Specifying `-s SOLUTION` is equivalent to specifying `-t solution -o SOLUTION`.


### -n, --dry-run

If specified, the conversions are performed in memory but nothing gets written to
disk.


### -f, --force

By default, if the OUTPUT path already exists, the conversion is skipped. Specifying `-f` forces existing files to be overwritten.


### -i, --interactive

If the OUTPUT path already exists, the user is prompted for confirmation before overwriting it.


### -h, --help

Show this help message and exit.


<!-- References -->

[placeholder variables]: https://spang-lab.github.io/urnc/placeholders.html
[keywords]: https://spang-lab.github.io/urnc/configuration.html#keywords
[target]: https://spang-lab.github.io/urnc/configuration.html#target
[tagged]: https://spang-lab.github.io/urnc/configuration.html#tags
