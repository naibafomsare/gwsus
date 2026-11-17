.. Gwsus documentation master file, created by
   sphinx-quickstart on Wed Nov  4 11:19:40 2026.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Gwsus documentation
===================

.. warning::

    This package and its documentation are under constant construction.

Predicting the behaviour of mirror suspensions is a mandatory task for the construction and operation
of gravitational-wave detectors. Before construction, it is necessary to ensure that the 
vibration isolation systems and payloads meet the requirements. And after construction, it is necessary to identify stray resonant motion during commissioning and astronomical observations. Gwsus aims to provide these capabilities and more.

One of the motivations for writing this software is to replace the one that is currently used in KAGRA for the same tasks. Despite the fact that such a package produces scientifically sound predictions, it has bugs and has not been maintained since 2015. It also has the disadvantage of requiring a license to run on Mathematica.
Gwsus is written in Python, which is a more accesible language, and is easy to maintain and use.


.. toctree::
   :maxdepth: 2
   :caption: Contents
   :includehidden:

   installation
   auto_examples/index
   theory
   api
   bibliography
