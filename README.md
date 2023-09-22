# URNC

UR FIDS notebook converter

## Installation

```sh
pip install urnc
```

Or update from an older version

```sh
pip install urnc --upgrade
```

## Usage for a course

This assumes your working directory is somewhere in a course directory

```sh
    cd my_urnc_course
```

Check the current course version

```sh
    urnc version 
```

Edit the course files.

See how the course will look for a student by converting your notebook files

```sh
    urnc convert . ./student
```

This will create a copy of all notebook files in the folder `student` and convert them to the student version.
You can check the output with jupyter. e.g

```sh
    cd student
    jupyter-lab
```

Once you are happy with your changes commit them. Make sure to delete the `student` folder again or add it to `.gitignore`.
In the clean repo use urnc to create a version commit.

```sh
    urnc version patch
    git push --follow-tags
```

The `--follow-tags` option is only required if git does not push tags by default.
We recommend configuring git to push tags automatically

```sh
    git config --global push.followTags true
```

The version is a [semver](https://semver.org). You can also run

```sh
    urnc version minor 
    urnc version major 
```

This will trigger the ci pipeline of the repo and create a student branch.

## Contribution FAQ

### Where to increase the version?

Only in [pyprocject.toml](pyproject.toml).

### When to tag a commit?

Whenever you want the Dockerfile to be rebuilt and pushed. Important: make sure your tag uses the same version as [pyproject.toml](pyproject.toml).
