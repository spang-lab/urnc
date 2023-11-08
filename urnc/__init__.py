"""
URNC (UR FIDS Notebook Converter)
=================================

URNC is a tool designed to convert notebook files within a course directory
into a format suitable for student use. It simplifies the process of preparing
and maintaining course materials by providing easy-to-use commands to check,
convert, and manage course versions.

Installation
------------
To install URNC, simply run:

.. code-block:: shell

    pip install urnc

To update an existing installation to the latest version:

.. code-block:: shell

    pip install urnc --upgrade

Usage
-----
To use URNC, navigate to your course directory and run the following commands:

Check the current course version:

.. code-block:: shell

    urnc version

To check for errors in course files without making changes:

.. code-block:: shell

    urnc check .

To convert notebook files to the student version and copy them to the 'student'
folder:

.. code-block:: shell

    urnc convert . ./student

Navigate to the 'student' directory to view the output using Jupyter:

.. code-block:: shell

    cd student
    jupyter-lab

Before committing your changes, ensure the 'student' folder is removed or added
to `.gitignore`. To create a version commit:

.. code-block:: shell

    urnc version patch
    git push --follow-tags

For configuring git to automatically push tags:

.. code-block:: shell

    git config --global push.followTags true

You can also increment the minor or major part of the version, following
semantic versioning (https://semver.org):

.. code-block:: shell

    urnc version minor
    urnc version major

This will also trigger the CI pipeline of the repository and create a student
branch.

Please note that URNC expects the working directory to be inside a course directory.

For further information and details on the usage, please refer to the official
documentation.

"""

from urnc import convert
from urnc import version
