Smartsheets Audit project documentation
=======================================

Overview
--------
The objective of this project is to be able to automatically audit our Smartsheets content.

We are not trying to create an exhaustive record of every cell's contents,
but a governance overview.

We want to have :
    * an up to date list of the objects stored on Smartsheets
    * who owns them
    * an idea of what sort of data might be contained in the object (columns, rows, widgets)
    * if it's getting its data from somewhere else - where (lineage)

Although it is possible to report lower level information (like the ranges referred to in cross sheet links)
it does not add considerable business value to do so, and the more cluttered the audit, the less usable it is.

It is also important that we do not store copies of any of the actual data contained in the audited objects,
so that we don't inadvertently create data privacy or confidentiality issues.

.. warning::
   Work in Progress - do not imagine that everything works !

   The code is in flux - we are still making key decisions about how best to execute the objectives.

   The code and the documentation have been published to support discussion about what we're doing and why,
   not because they are finished.

Links
-----
   * `Smartsheet API documentation <https://smartsheet.redoc.ly>`_
   * `Smartsheet Python SDK documentation <http://smartsheet-platform.github.io/smartsheet-python-sdk/index.html>`_

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   devplans
   devnotes
   audit_file
   project_status
   python_code
   python_stack
   glossary

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
