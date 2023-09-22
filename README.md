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

## Contribution

First check that you have the lateste version of this repo

```sh
    git pull
    urnc version --self

```

If you want to make changes to `urnc` update the python files in `urnc` and commit the changes.
Afterwards use

```sh
    urnc version --self patch
    # or urnc version --self minor 
    # or urnc version --self major 
    git push --follow-tags
```

To create a tagged commit and trigger the Githup actions.

The `--follow-tags` option is only required if git does not push tags by default.
We recommend configuring git to push tags automatically

```sh
    git config --global push.followTags true
```

