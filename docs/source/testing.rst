Testing
=======

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
