Vensim Translation
==================

PySD parses a vensim '.mdl' file and translates the result into python, creating a new file in the
same directory as the original. For example, the Vensim file :download:`Teacup.mdl<../../tests/vensim/Teacup.mdl>`:

.. literalinclude:: ../../tests/vensim/Teacup.mdl
   :lines: 1-51

becomes :download:`Teacup.py<../../tests/vensim/Teacup.py>`:

.. literalinclude:: ../../tests/vensim/Teacup.py
   :language: python

This allows model execution independent of the Vensim environment, which can be handy for deploying
models as backends to other products, or for performing massively parallel distributed computation.

These translated model files are read by PySD, which provides methods for modifying or running the
model and conveniently accessing simulation results.


Translated Functions
--------------------

Ongoing development of the translator will support the full subset of Vensim functionality that
has an equivalent in XMILE. The current release supports the following functionality:

.. include:: supported_vensim_functions.rst

Additionally, identifiers are currently limited to alphanumeric characters and the dollar sign $.

Future releases will include support for:

- subscripts
- arrays
- arbitrary identifiers

There are some constructs (such as tagging variables as 'suplementary') which are not currently
parsed, and may throw an error. Future releases will handle this with more grace.
