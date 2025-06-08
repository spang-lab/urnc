# CI

Run the urnc CI pipeline without pushing

## Usage

    urnc student [--help]

## Description

Performs the same steps as `urnc ci` to create a new "student" version from the
current course. However, unlike `urnc ci`, this new student version is
NOT pushed to the "student" remote repository.

This command allows you to test the output of `urnc ci` without uploading (pushing) a new version.

## Options:

### --help

Show this message and exit.
