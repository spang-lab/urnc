# Convert

Converts input notebooks to the specified target formats.


## Usage

```
urnc convert [-f|-n|-i] [-t TARGET] [-s SOLPATH] [-o OUTPATH] INPUT
```

## Description

Notebook conversion by `urnc` happens in two stages:

1. All lines of all input notebooks are checked for [keywords].
   If a keyword is found, the containing cell is [tagged] accordingly.
2. All tagged cells are processed according to the specified target format.

This two-stage approach allows manual tagging of cells in addition to the use of
keywords to configure the conversion behaviour. See [-t, --target
TARGET](#-t---target-target) for a description of the effect of each tag on the
conversion targets.


## Options


### INPUT

Path to a single input notebook or a directory containing notebooks.
If INPUT is a directory, all notebooks in the directory are converted recursively.


### -t, --target TARGET

Specifies the conversion target, i.e., the type of conversion to be performed.
This option can be used multiple times to specify multiple targets.
Valid targets are: `student`, `solution`, `execute`, `clear`, and `fix`.
Every target can contain an additional, colon-seperated output path, e.g.
`student:out` or `solution:C:\tmp`.
Paths can contain [placeholder variables](../placeholders.md).
If not output path is provided, a target-specific default location is used, as
described in [Plain Directory Paths](../placeholders.md#plain-directory-paths).
Depending on the target, the following actions are performed for each input
notebook:

1. `student`:
    1. Tag cells matching `# <solution-keyword>` as `solution`.
    2. Tag cells matching `# <skeleton-keyword>` as `skeleton`.
    3. Find cells tagged as `solution` and/or `skeleton` but not as `ignore`.
    4. Remove `solution` lines and uncomment `skeleton` lines from these cells.

2. `solution`:
    1. Tag cells matching `# <skeleton-keyword>` as `skeleton`.
    2. Find cells tagged as `skeleton`, but not as `ignore`.
    3. Uncomment `skeleton` lines in these cells.

3. `execute`:
    1. Tag cells matching `# <solution-keyword>` as `solution`.
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


### -o, --output OUTPATH

Path for storing the output of the [`student` target](#-t---target-target).
Can be a file or directory path.
If `-o OUTPATH` is not specified, `out/` is used by default.
Supports [placeholder variables](../placeholders.md).

Remark: specifying `-o OUTPUT` is equivalent to specifying `-t student:OUTPATH`.

### -s, --solution SOLPATH

Path for storing the output of the [`solution` target](#-t---target-target).
Can be a file or directory path.
If `-s SOLPATH` is not specified, the solution target is not generated (unless
specified via `-t solution`).
Supports [placeholder variables](../placeholders.md).

Remark: specifying `-s SOLPATH` is equivalent to specifying `-t solution:SOLPATH`.


### -n, --dry-run

If specified, the conversions are performed in memory but nothing gets written
to disk.


### -f, --force

By default, if an output path exists already, the conversion is skipped.
Specifying `-f` forces existing files to be overwritten.


### -i, --interactive

If an output path exists already, the user is prompted for confirmation before
overwriting it.


### -h, --help

Show this help message and exit.
