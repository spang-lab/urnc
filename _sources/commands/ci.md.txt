# CI

Run the urnc CI pipeline.

## Usage

    urnc ci [--help]

## Description

Performs the following steps to create and publish a new "student" version:

1. Clones or pulls STUDENT_REPO as STUDENT_PATH
2. Deletes all non-hidden files in STUDENT_PATH
3. Copyies all non-hidden files from ADMIN_PATH to STUDENT_PATH
4. Converts all notebooks in STUDENT_PATH according to CONVERT_CONFIG
5. Update STUDENT_PATH/.gitignore according to GIT_EXCLUDES
6. Commit and push the changes

All configuration values mentioned above are taken from the course [config
file](../configuration.md):

ADMIN_PATH     = config["base_path"]
STUDENT_REPO   = config["git"]["student"]
STUDENT_PATH   = config["git"]["output_dir"]
GIT_EXCLUDES   = config["git"]["exclude"]
CONVERT_CONFIG = config["convert"]

For the full list of configuration values, see
https://spang-lab.github.io/urnc/configuration.html

To test the pipeline locally, without actually pushing to the remote, use
command `urnc student`.

## Options:

### --help

Show this message and exit.

## Limitations

This command requires config option [git.student](../configuration.md#student)
to be properly defined, or the push will fail.
