Audit File Structures
=====================

Smartsheet audit file
---------------------
:id: unique identifier of the object (Sheet)
:name: name of the object
:owner: email address of the the person who owns the object
:workspace: name of the workspace the object is in (or 'None' if it's a personal sheet)
:crossSheetReferences: list of the names of sheets that this sheet gets data from
:createdAt: date/time the object was first created
:modifiedAt: date/time the object was last modified
:permalink: url of the object
:rowCount: number of rows in the object
:columnTitles: list of the column titles

Dashboard audit file
--------------------
:id: unique identifier of the object (Dashboard)
:name: name of the object
:workspace: name of the workspace the object is in (or 'None' if it's a personal sheet)
:sheetReferences: list of the names of sheets that this dashboard gets data from
:createdAt: date/time the object was first created
:modifiedAt: date/time the object was last modified
:permalink: url of the object
:widgetCount: number of widgets in the object
:widgetTitles: list of the widget titles (for widgets that have a title property)

Report audit file
-----------------
:id: unique identifier of the object (Report)
:name: name of the object
:workspace: name of the workspace the object is in (or 'None' if it's a personal sheet)
:sourceSheets: list of the names of sheets that this sheet gets data from
:createdAt: date/time the object was first created
:modifiedAt: date/time the object was last modified
:permalink: url of the object
:rowCount: number of rows in the object
:columnTitles: list of the column titles