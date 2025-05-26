# Configuration

Most urnc commands operate on a complete course, containing multiple jupyter notebooks (e.g. `urnc student`, `urnc version` or `urnc ci`).

The exact behaviour of these commands can be configured by editing the `config.yaml` file in the course root directory. This file is created automatically when you run `urnc init` for the first time.

An example `config.yaml` is given in section [Example Config](#example-config). Descriptions for each field are provided in section [Configuration Options](#configuration-options).


## Example Config

```yaml
name: "URNC Example Course"
version: "1.0.4"
description: "Example course demonstrating the use of URNC (https://github.com/spang-lab/urnc)"
authors:
    - {name: "Tobias Schmidt", email: tobias.schmidt331@gmail.com}
    - {name: "Michael Huttner", email: michael@mhuttner.com}
git:
    student: "https://USERNAME:PASSWORD@github.com/spang-lab/urnc-example-course-public.git"
    output_dir: "out"
    exclude:
    - "config.yaml"
    - "README.md"
    - "assignments/*"
    - {pattern: "!assignments/01*.ipynb", after: "2023-10-02"}
    - {pattern: "!assignments/02*.ipynb", after: "2023-10-09"}
convert:
    keywords:
        assignment: ["Lab", "Assignment"]
        skeleton: ["Skeleton"]
        solution: ["Solution"]
    targets:
        - {type: "student", path: "{nb.abspath}"}
        - {type: "solution", path: "{nb.absdirpath}_solutions/{nb.name}"}
    ignore: []
    tags:
        solution: "solution"
        skeleton: "skeleton"
        assignment: "assignment"
        assignment-start: "assignment-start"
        ignore: "ignore"
        no-execute: "no-execute"
jupyter:
    version: 1.13.0
    links:
        - {name: Webpage, url: https://spang-lab.github.io/urnc-example-course}
        - {logo: "https://placehold.co/64"}
        - {pull_url: https://github.com/spang-lab/urnc-example-course-public.git}
    users:
        - "mhuttner"
        - "tschmidt"
```

## Configuration Options


### name

Name of the course as free text.


### semester

Semester of the course as free text.


### version

Semantic version of the course, e.g., '1.0.0'.


### description

Description of the course as free text.


### authors

List of authors. Each author must be a dictionary with a `name` and
`email` field.


### git

Dictionary of the following git-related options: [student](#student), [output_dir](#output_dir), [exclude](#exclude).


#### student

URL to the public repository where course materials are published for students. The URL must include valid credentials, as it is used by `urnc ci` to push the processed course materials (e.g., notebooks without solutions). If your main repository is public, we recommend using CI tools like [GitLab CI/CD Variables](https://docs.gitlab.com/ee/ci/variables/) or [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets) to securely manage credentials and inject them at runtime during pipeline execution.


#### output_dir

Directory where the processed course materials are stored when calling `urnc student` or `urnc ci`. If [`git.student`](#student) is provided, the given repository will be cloned into this directory before starting the conversions. It's highly recommended to add this directory to your `.gitignore`.


#### exclude

List of files or directories to exclude from publishing by `urnc ci`. Each entry is interpreted as a glob pattern. Entries can be either a string or a dictionary. If a dictionary is used, it must include a `pattern` field and can optionally include `after` and `until` fields to specify time-based conditions. At runtime, entries meeting the time conditions will be appended to the `.gitignore` file in the `output_dir`, ensuring they are ignored during publishing.


### convert

Dictionary of the following conversion-related options: [keywords](#keywords), [targets](#targets), [ignore](#ignore), and [tags](#tags).


#### keywords

Keywords used to categorize lines within each notebook. Currently, the following categories are supported: `assignment`, `skeleton`, and `solution`. Lines matching `^\s*(#{1,6})\s*\b{keyword}\b.*$` start the respective category. Lines matching `^\s*(#{1,6})\s*$` end the current category. Depending on the conversion target, lines of a certain type are either removed, transformed, or left unchanged in the notebook. Example: if you configure `solution: "SOL"` (i.e. you set the `solution` keyword to `SOL`) the following cell would be tagged as `solution` and lines 2-4 would be removed in the `student` notebook:

```python
# Enter your solution here   # left unchanged
### SOL                      # gets removed
sum(range(1, 100))           # gets removed
###                          # gets removed
```


#### targets

List of conversion targets created by `urnc ci` and `urnc student`.
Each target must be a dictionary with fields `type` and `path`.
Field `type` defines what kind of conversion is performed.
Supported types are: `student`, `solution`, `execute`, `clear`, `fix`.
Field `path` defines where the converted notebooks get saved and can contain [placeholder variables](placeholders.md#placeholder-variables).

Conversions of individual notebooks can be tested using the commands shown in the example below:

```bash
urnc convert --output student_version.ipynb input_notebook.ipynb
urnc convert --solution solution_version.ipynb input_notebook.ipynb
urnc check --clear input_notebook.ipynb # clears output cells inplace
urnc check --image input_notebook.ipynb # fixes image paths inplace
urnc execute input_notebook.ipynb
```


#### ignore

List of glob patterns to ignore during conversion.
This is different from [`git.exclude`](#exclude), because it suppresses the actual conversion of the notebook, whereas `git.exclude` only suppresses the publishing of the notebook.


#### tags

Dictionary of tags used by `urnc` to categorize cells in the notebook.
Cell categories used by `urnc` are `solution`, `skeleton`, `assignment`, `assignment-start`, `ignore`, and `no-execute`.
The default values for tagging such cells are:

```yaml
tags:
    solution: "solution"
    skeleton: "skeleton"
    assignment: "assignment"
    assignment-start: "assignment-start"
    ignore: "ignore"
    no-execute: "no-execute"
```

See [urnc convert](commands/convert.md) for details on how each tag affects the conversion process for each target type.


### jupyter

Dictionary of the following Jupyter/JupyterHub-related options: [version](#version), [links](#links), [users](#users).

This field is not used by `urnc` directly, but by the script for generating a JupyterHub server list at runtime.


#### version

Specifies the version of the image used by JupyterHub.


#### links

List of links displayed below the course name in the JupyterHub server list.
Each link must be given as a dictionary with a `name` and `url` field, except for the following two special cases:

1. If a dictionary contains a `logo` field, that logo will be displayed next to the course name in the JupyterHub server list. Other dictionary fields are ignored in this case.

2. If a dictionary contains a `pull_url` field, that URL will be used by `urnc pull` to clone or pull the course repository inside the container before the user is redirected to the JupyterHub server. Other dictionary fields are ignored in this case.


#### users

List of users allowed to access this profile on the JupyterHub server.
