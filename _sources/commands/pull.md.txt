# Pull

Pull GIT_URL and automatically merge in local changes.

## Usage

    urnc pull [-o OUTPATH] [-b BRANCH] [-d DEPTH] [-l LOGPATH] [GIT_URL]

## Description

Pulls from GIT_URL and automatically merges remote and local changes.
If OUTPUT does not exist yet, a clone is performed instead.
This command wraps `git pull` and `git merge -Xours`, with additional automatic merging behavior.

The automatic merging works the same way as in [nbgitpuller](https://nbgitpuller.readthedocs.io/en/latest/topic/automatic-merging.html). Unlike nbgitpuller, `urnc pull` does not hide the remote URL, as urnc expects the remote repository (the "student" repository) to be publicly accessible. This allows Git-savvy users to access the full version history, which is not easily possible with nbgitpuller.

If you need to pull from private repositories without exposing access tokens, we recommend using [nbgitpuller](https://nbgitpuller.readthedocs.io/en/latest/) instead of `urnc pull`.

### -o, --output OUTPATH

The name of the output folder

### -b, --branch BRANCH

The branch to pull

### -d, --depth DEPTH

The depth for git fetch

### -l, --log-file PATH

The path to the log file

### --help

Show this message and exit
