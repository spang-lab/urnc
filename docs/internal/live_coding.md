# Usage

This guide explains how to use urnc to create and manage a course repository for tutors and students. The workflow involves

1. Creating an "admin" repository with lectures, assignments and solutions
2. Publishing a corresponding "student" repository where the solutions have been removed
3. Cloning the student repository to a local machine
4. Checking the notebooks for errors

## 1. Initialize a New Course

To start a new course, use the `urnc init` command. This initializes a new "admin" repository with a default configuration and an example notebook.

```sh
urnc init --template=full "My Example Course"
```

This creates a directory named after the course, initializes a Git repository, and sets up the following file structure:

```none
<path>
├── .git
├── .gitignore
├── config.yaml
├── images
│   ├── blue_rectangle.png
│   └── red_circle.png
├── lectures
│   └── week1
│       ├── lecture1.ipynb
│       └── lecture2.ipynb
└── assignments
    └── week1.ipynb
```

The `config.yaml` file contains metadata and configuration and looks roughly like this:

```yaml
name: "My Example Course"
semester: "semester"
description: "description for your course"
version: "0.1.0"
authors: [{name: "Your Name", email: "YourEmail@host.com"}]
git: {student: "Link to student repo"}
output_dir: "out"
exclude: ["config.yaml", "container/"]
```

The `ipynb` files are short example notebook showcasing various features of
urnc. `lecture1.ipynb` look e.g. as follows:

    +----------------------------+----------+
    | # Lecture 1                | markdown |
    | ---------------------------+----------+
    | ## Assignment 1            | markdown |
    | ---------------------------+----------+
    | Print Hello World          | markdown |
    | ---------------------------+----------+
    | ### Solution               |          |
    | print('Hello World')       |          |
    | ### Skeleton               | code     |
    | # Enter your solution here |          |
    | ###                        |          |
    +----------------------------+----------+

## 2. Create and Publish the Student Version

To create a student version of the course (without solutions), use the `urnc student` command:

```sh
urnc student
```

This generates a student version locally. To publish it, use the `urnc ci` command, which pushes the student version to the remote repository:

```sh
urnc ci
```

Before publishing, ensure the course version is updated using:

```sh
urnc version patch
```

Other versioning options include `minor` and `major`.

The `urnc student` and `urnc ci` commands use conversion targets defined in `config.yaml`. These targets specify how notebooks are processed (e.g., removing solutions). For more details, see Chapter 4.

## 3. Pull the Student Version

To clone the student repository, use the `urnc clone` command:

```sh
urnc clone <student-repo-url>
```

To update an existing local copy of the student repository, use:

```sh
urnc pull
```

## 4. Convert Notebooks

The `urnc convert` command processes notebooks based on specified targets. For example, to convert all notebooks in the current directory and output them to a `student` folder:

```sh
urnc convert . ./student
```

Conversion targets can include removing solutions, clearing outputs, or executing notebooks.

## 5. Check Notebooks

To check notebooks for formal errors, use the `urnc check` command, e.g.:

```sh
urnc check .         # checks all notebooks in the current dir
urnc check --clear . # additionally clears outputs
urnc check --image . # additional checks image paths
```

To check for coding errors, you can execute notebooks and save their outputs using the `urnc execute`, e.g.

```sh
urnc execute .
```

This ensures that all code cells run without errors and outputs are up-to-date.
