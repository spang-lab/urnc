# Execute

Execute INPUT notebooks

## Usage

    urnc execute [-o OUTPUT] [--help] [INPUT]

## Description

Executes INPUT notebooks and writes the resulting notebooks (inkl. outputs of code cells) to the OUTPUT path.

This command is a shortcut for `urnc convert -t execute`. To be precise, the following two commands are equivalent:

```bash
urnc execute INPUT
urnc convert -t execute INPUT
```

And these commands are equialent as well:

```bash
urnc execute -o OUTPUT INPUT
urnc convert -t execute:OUTPUT INPUT
```

## Options

### -o, --output OUTPUT

The name of the output file or folder.

### --help

Show this message and exit.
