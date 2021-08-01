Dev Notes
=========

.. note:: This work is unfinished. Here, the author attempts to record what he wants the end result to look like.

Refactor to use recursive logic and the SDK throughout
------------------------------------------------------

Workspaces and Folders are Containers.

Containers contain Folders and Collections.

A Container which has a parent is a Folder.
The object calling a child container should pass its own ``container_path`` to the child.

For example:

* ``Workspace A`` has a folder called ``Folder1``
* It should pass 'Workspace A' to `Folder1` as its container_path.
* ``Folder1``'s container_path becomes 'Workspace A/Folder1'.
* If ``Folder1`` has a child ``FolderQ``, it should pass 'Workspace A/Folder1' as its folderpath
  and
* ``FolderQ`` should report its container_path as 'Workspace A/Folder1/FolderQ'

(Technically the Organisation is the parent of a Workspace,
but only the system admin has access to Organisation level info)

Containers orchestrate an audit across their collections : Sheets, Dashboards, Reports.

Collections (Sheets, Dashboards, Reports) have an ``audit`` method to audit the objects they contain
and return an audit report as a dict.

.. code-block:: json

   {"container_path": "Data Management/MonthEnd Reporting",
    "collection_type": "reports",
    "results": [{"id": 12345678987654321,
                 "name": "MoM Change by Business Area",
                 "sourceSheets": ["Business Areas", "MonthEnd Reporting Datasheet"],
                 "createdAt" : "2020-04-26T13:25:32-00:00",
                 "modifiedAt": "2021-07-31T08:14:23-00:00",
                 "permalink": "https://app.smartsheet.com/reports/XXXxxxXXXxxxXXXXXXXxWWWWWWWWWwWWWWWWWWWW",
                 "rowCount": 106,
                 "columnTitles": ["Primary","Sheet Name","Created","Data Count"]}]}

The ultimate parent container (the workspace) collates all the audit reports from all of the collections that it or its descendents contain::

   Container
       |
       |_Container
       |
       |_Sheets
       |
       |_Reports
       |
       |_Dashboards

