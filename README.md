# SmartsheetAudit
**Data governance audit of a Smartsheets account**

The objective of this project is to be able to automatically audit our Smartsheets content.

We are not trying to create an exhaustive record of every cell's contents,
but a governance overview.

We want to have :
    * an up to date list of the objects stored in each Smartsheets workspace
    * who owns them (where available)
    * an idea of what sort of data might be contained in the object (columns, rows, widgets)
    * if it's getting its data from somewhere else - where (lineage)

**Constraints**

Although it is possible to report lower level information (like the ranges referred to in cross sheet links)
it does not add considerable business value to do so, and the more cluttered the audit, the less usable it is.

The audit is currently only covering workspaces - it does not audit Smartsheets saved in users' private Home folders.

We do not make copies of any of the data inside the audited objects, (cell contents, widget values)
so that we don't inadvertently create data privacy or confidentiality issues.
We only record metadata about the ownership, structure and data sources of each object.
