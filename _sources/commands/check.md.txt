# Check

Check INPUT notebooks for errors

## Usage

    urnc check [-q] [-c] [-i] [INPUT]

## Description

Calling `urnc check` without any additional arguments is essentially the same as calling `urnc convert --dry-run -t "student"`, with more outputs shown by default. I.e., a conversion is attempted, and all corresponding messages and warnings are printed, but nothing gets written to disk.

## Options

### INPUT

Path to a single input notebook or a directory containing notebooks. If INPUT is
a directory, all notebooks in the directory are checked recursively.

### -q, --quiet

Only show warnings and errors.

### -c, --clear

DEPRECATED. Use `urnc convert -t clear INPUT` instead.

Removes outputs from input notebooks. This modifies all input notebooks in
place.

### -i, --image

DEPRECATED. Use `urnc convert -t fix INPUT` instead.

Fix image paths in input notebooks. This modified all input notebooks in place.

### --help

Show this message and exit.
