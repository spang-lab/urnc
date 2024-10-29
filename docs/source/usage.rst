Usage
=====

All following commands assume your working directory is somewhere inside a course directory:

.. code-block:: sh

   cd my_urnc_course

Check the current course version:

.. code-block:: sh

   urnc version

Edit the course files.

Check for errors only:

.. code-block:: sh

   urnc check .

See how the course will look for a student by converting your notebook files:

.. code-block:: sh

   urnc convert . ./student

This will create a copy of all notebook files in the folder `student` and convert them to the student version.
You can check the output with jupyter, e.g:

.. code-block:: sh

   cd student
   jupyter-lab

Once you are happy with your changes commit them. Make sure to delete the `student` folder again or add it to `.gitignore`. In the clean repo use urnc to create a version commit:

.. code-block:: sh

   urnc version patch
   git push --follow-tags

The `--follow-tags` option is only required if git does not push tags by default. We recommend configuring git to push tags automatically:

.. code-block:: sh

   git config --global push.followTags true

The version is a `semver <https://semver.org>`_. You can also run:

.. code-block:: sh

   urnc version minor
   urnc version major

This will trigger the ci pipeline of the repo and create a student branch.
