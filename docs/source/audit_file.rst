Audit Report Structures
=======================


Example JSON Audit Report
-------------------------
.. code-block:: json

    {
      "container_id": 20000000000000000,
      "name": "ExampleWorkspaceName",
      "container_type": "workspace",
      "container_path": "ExampleWorkspaceName",
      "sheets": [
        {
          "id": 6552838803037655,
          "name": "Imaginary Smartsheet Title",
          "owner": "fictitious.person@domain_name.com",
          "cross_sheet_references": null,
          "created_at": "2021-07-31T11:15:41+00:00",
          "modified_at": "2021-07-31T15:41:37+00:00",
          "permalink": "https://app.smartsheet.com/sheets/AaaAaaAAaaa0Aa0a0a00A00AaAAA00AaAAaaAaa0",
          "total_row_count": 26,
          "column_titles": ["Task Name", "Due Date", "Done", "Assigned To", "Status", "Comments"]
        }
      ],
      "reports": [],
      "dashboards": [],
      "folders": [
        {
          "container_id": 474233297711736,
          "name": "Data Management",
          "container_type": "folder",
          "container_path": "ExampleWorkspaceName/One Folder",
          "sheets": [
            {
              "id": 896842959710406,
              "name": "audit_sheets",
              "owner": "fictitious.person@domain_name.com",
              "cross_sheet_references": null,
              "created_at": "2021-07-31T11:08:42+00:00",
              "modified_at": "2021-07-31T11:14:45+00:00",
              "permalink": "https://app.smartsheet.com/sheets/hHhHhHhH9H99hHhHhH9Hh999hHh9hHh9hHhHhH9H",
              "total_row_count": 15,
              "column_titles": ["id", "name", "workspace", "crossSheetReferences", "createdAt", "modifiedAt", "permalink",
                                "rowCount", "columnTitles"]
            },
            {
              "id": 322220912583146,
              "name": "audit_dashboards",
              "owner": "moniker.pseudonym@domain_name.com",
              "cross_sheet_references": null,
              "created_at": "2021-07-31T11:09:31+00:00",
              "modified_at": "2021-07-31T11:10:24+00:00",
              "permalink": "https://app.smartsheet.com/sheets/CccCC8C8cc8cCcCccc8c8CcC8CccCccc888ccCc8",
              "total_row_count": 1,
              "column_titles": ["id", "name", "workspace", "sheetReferences", "createdAt", "modifiedAt", "permalink",
                                "widgetCount", "widgetTitles"]
            },
            {
              "id": 977478336411229,
              "name": "audit_reports",
              "owner": "meaningless.drivel@emaildomain.co.uk",
              "cross_sheet_references": null,
              "created_at": "2021-07-31T14:23:26+00:00",
              "modified_at": "2021-07-31T15:24:16+00:00",
              "permalink": "https://app.smartsheet.com/sheets/xXxXxXxX9X99xXxXxX9Xx999xXx9xXx9xXxXxX9X",
              "total_row_count": 17,
              "column_titles": ["id", "name", "workspace", "sourceSheets", "createdAt", "modifiedAt", "permalink",
                                "rowCount", "columnTitles"]
            }
          ],
          "reports": [],
          "dashboards": [],
          "folders": []
        }
      ]
    }

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