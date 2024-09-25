Contributing
============

First check that you have the latest version of this repo:

.. code-block:: sh

   git pull
   urnc version --self

If you want to make changes to `urnc` update the python files in `urnc` and test your changes as described in page `Testing <testing>`_. When you are happy with your changes, push them to Github. Afterwards use the following commands to create a tagged commit and trigger the Github actions:

.. code-block:: sh

   urnc version --self patch
   # or urnc version --self minor
   # or urnc version --self major
   git push --follow-tags

The `--follow-tags` option is only required if git does not push tags by default. We recommend configuring git to push tags automatically:

.. code-block:: sh

   git config --global push.followTags true
