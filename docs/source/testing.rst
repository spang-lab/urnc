Testing
=======

Regression tests
----------------

We use `pytest <https://docs.pytest.org/en/latest/>`_ for regression testing. To run the full regression test suite, simply call ``pytest --tb=short`` from the root of the repository **after package installation**. The tests are located in folder `tests <https://github.com/spang-lab/urnc/tree/main/tests>`_. To run a specific test, you can use the ``-k`` flag, e.g. ``pytest -k test_version``. For a list of existing tests see `test <https://github.com/spang-lab/urnc/tree/main/tests>`_. To avoid having to install the package repeatedly after each change, we recommend performing an `editable install <https://setuptools.pypa.io/en/latest/userguide/development_mode.html>`_ using ``pip install -e .``. This allows you to modify the source code and run the tests directly without needing to reinstall the package. Note, however, that it is still required to reinstall the package whenever you modify the `pyproject.toml <https://github.com/spang-lab/urnc/tree/main/pyproject.toml>`_ file.

For now, you also need to have access to `<https://git.uni-regensburg.de/fids>`_ to run the regression tests, i.e.

#. you need to be a member of the FIDS organization at the Gitlab Server of the University of Regensburg and
#. you need to be connected to the university network

In the future, we might replace the real FIDS courses with public dummy courses. In case your interested in this feature, please open a corresponding issue.

.. code-block:: bash

   # All commands for copy pasting
   git clone https://github.com/spang-lab/urnc.git
   cd urnc
   pip install -e .
   pytest --tb=short -k test_version # run tests/test_version.py only
   pytest --tb=short # run all tests/test*py files

Testing urnc on real data
-------------------------

The easiest way to test `urnc <https://github.com/spang-lab/urnc>`_ updates on real data is to:

#. Clone urnc
#. Clone your course of interest, e.g. `urnc-example-course <https://github.com/spang-lab/urnc-example-course>`_
#. Add the folder you cloned `urnc` into to your `PYTHONPATH`
#. Call urnc as usual

The corresponding commands are something like:

.. code-block:: bash

   # Clone urnc and urnc-example-course
   git clone https://github.com/spang-lab/urnc.git
   git clone https://github.com/spang-lab/urnc-example-course.git

   # Add urnc to your pythonpath
   export "PYTHONPATH=$(pwd)/urnc" # bash/zsh syntax
   $env:PYTHONPATH = "$(pwd)\urnc" # powershell syntax

   # Make some updates to ./urnc/urnc/*.py

   # Call urnc as usual
   pushd urnc-example-course
   urnc student
   popd