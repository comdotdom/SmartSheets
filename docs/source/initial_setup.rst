Initial Setup
=============

smartsheets.env
---------------
SmartsheetAudit expect to find a file called **smartsheets.env** in the same directory as the code.

This file contains the API key the programme will use and the paths for the folders where it will save files.

It takes the format:

.. code-block:: text

   SMARTSHEET_ACCESS_TOKEN = "6ghdlrnfklwJEVdbwu4ndlfin4kfjsifbekHD"
   ROOT_FOLDER = "~/SmartSheetAudit"
   JSON_FOLDER = "~/SmartSheetAudit/data/json"
   TEXT_FOLDER = "~/SmartSheetAudit/data/txt"

Please edit this file and replace this false API key with your own Smartsheet API key and
these false paths with the paths to your SmartsheetAudit installation and to the two directories
where you will store JSON files and pipe-delimited text files.
