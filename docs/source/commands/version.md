# Version

Manage the semantic version of your course

## Usage

    urnc version [OPTIONS] [ACTION]

## Options

### ACTION

Which action to perform.
Can be show, major, minor, patch or prerelease.
The result of each action is described in the following listing:

- show: prints the current course version
- major: increase the major part of the current version
- minor: increase the minor part of the current version
- patch: increase the patch part of the current version
- prerelease: increase the prerelease part of the current version

### --self

Print urnc's own version. Same as `urnc --version`.

### --help

Show this message and exit.

## Examples

```bash
# Assuming the current version defined in config.yaml is 2.1.6
urnc version show  # would print 2.1.6
urnc version major # would change the version to 3.0.0
urnc version minor # would change the version to 2.2.0
urnc version patch # would change the version to 2.1.7
urnc version pre-release # would change the version to 3.0.0-rc1
```