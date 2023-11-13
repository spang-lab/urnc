Documentation
=============

Documentation for this package is generated automatically upon pushes to main using `sphinx <https://www.sphinx-doc.org/en/master/index.html>`_ with extensions `autodoc <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html>`_ and `myst_parser <https://myst-parser.readthedocs.io/en/latest/>`_. The relevant commands to generate the documentation pages locally, are listed in the following:

.. code-block:: bash

   # Install sphinx and myst-parser (for markdown support)
   pip install sphinx myst-parser sphinx_rtd_theme

   # Build documentation
   cd docs
   make html # other formats are: epub, latex, latexpdf
