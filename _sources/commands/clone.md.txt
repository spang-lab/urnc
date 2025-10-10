# Clone

Clone GIT_URL to OUTPATH.
If OUTPATH exists already, call `git pull --fast-forward` within it.

## Usage

    urnc clone [-o OUTPATH] [-b BRANCH] [GIT_URL]

## Options:

### -o, --output OUTPATH

The name of the output folder

### -b, --branch BRANCH

The branch to pull

### -d, --depth DEPTH

The depth for git fetch as integer.

### -l, --log-file LOGPATH

The path to the log file

### --help

Show this message and exit.
