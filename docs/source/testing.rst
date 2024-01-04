Testing
=======

Test Suite
----------

We use `pytest <https://docs.pytest.org/en/latest/>`_ together with `freezegun <https://github.com/spulec/freezegun>`_ and `pytest-cov <https://pypi.org/project/pytest-cov/>`_ for testing. To run the full test suite, install the mentioned packages and urnc and then call ``pytest --runslow`` from the root of the repository. The tests are located in folder `tests <https://github.com/spang-lab/urnc/tree/main/tests>`_. To skip the slow tests, omit the ``--runslow`` flag. To run a specific test, use the ``-k`` flag, e.g. ``pytest -k test_version``. To avoid having to install the package repeatedly after each change, we recommend performing an `editable install <https://setuptools.pypa.io/en/latest/userguide/development_mode.html>`_ using ``pip install -e .``. This allows you to modify the source code and run the tests for the modified version without needing to reinstall the package. Note, however, that it is still required to reinstall the package whenever you modify the `pyproject.toml <https://github.com/spang-lab/urnc/tree/main/pyproject.toml>`_ file.

For now, you also need to have access to `<https://git.uni-regensburg.de/fids>`_ to run the regression tests, i.e.

#. you need to be a member of the FIDS organization at the Gitlab Server of the University of Regensburg and
#. you need to be connected to the university network

In the future, we might replace the real FIDS courses with public dummy courses. In case your interested in this feature, please open a corresponding issue.

.. code-block:: bash

   # All commands for copy pasting
   git clone https://github.com/spang-lab/urnc.git # clone urnc
   cd urnc
   pip install -e . # install urnc in editable mode
   pip install pytest pytest-cov freezegun PyYAML # install testing dependencies
   pytest --tb=short # run all fast tests and show short traceback
   pytest --runslow  # run all tests/test*py files
   pytest -k test_version # run tests/test_version.py only
   pytest -s # show stdout of commands during tests (useful for debugging)

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
