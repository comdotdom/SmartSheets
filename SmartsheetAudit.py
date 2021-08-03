"""
SmartsheetAudit

:author:  Dominic Gittins
:contact: dominic@gittins.co.uk
:version: 0.2
:date:    02-Aug-2021
"""

import json
# import logging
# import os
from pprint import pprint
from envparse import env
from tqdm import tqdm
import smartsheet
from slugify import slugify
from datetime import datetime


SHEET_NAME_MAP = {}
JSON_FOLDER = ''


class SmartsheetAudit:
    """
    **Audit runner** - this is the class used to run a Smartsheet audit.

    Creates a list of all the workspaces visible to the API key owner and
    sets up a SmartContainer for each workspace.

    Instructs the SmartContainer to audit the workspace and saves the results.

    Uses environment variables for API key and local filepaths

    **Usage**

    .. code-block:: python

       app = SmartSheetAudit()
    """
    def __init__(self):
        env.read_envfile('smartsheets.env')
        JSON_FOLDER = env('JSON_FOLDER')
        self.smart = smartsheet.Smartsheet()
        response = self.smart.Workspaces.list_workspaces(include_all=True)
        self.workspaces = response.data
        # CREATE GLOBAL SHEET_NAME_MAP LOOKUP
        sheet_list = self.smart.Sheets.list_sheets(include_all=True)
        for s in sheet_list.data:
            SHEET_NAME_MAP[s.id] = s.name

        for w in self.workspaces:
            wkspce = SmartContainer(container_id=w.id)
            w = wkspce
            w.audit()
            audit_date = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{JSON_FOLDER}/{slugify(w.name)}-{audit_date}.json"
            with open(filename, 'w') as f:
                json.dump(w.audit_report, f)


class SmartContainer:
    """
    :param container_id: The workspace_id or folder_id we are going to audit
    :param parent: The container_path of the calling SmartContainer (left blank when called for a workspace)

    Workspaces and Folders can contain sheets, dashboards, reports and (sub-)folders.

    SmartContainer is a base class which may be a Workspace or a Folder,
    but which adds metadata collection (audit) capability,
    and the audit_results property to store the results of the audit.

    A SmartContainer will have a ``container_path`` property which shows a breadcrumb trail
    of its own folder structure - starting at the ultimate parent Workspace.

    Running the ``audit`` method conducts a data governance audit of the workspace
    and stores its results in the ``audit_report`` dict property.
    """

    def __init__(self, container_id: int, parent: str = None):
        """
        Gets listings of all the sheets, dashboards, reports and folders in this container from the smartsheet API.
        """
        self.smart = smartsheet.Smartsheet()
        self.parent: str = parent
        self.sheets = None
        self.reports = None
        self.sights = None
        self.folders = []

        if self.parent:
            self.container_type = 'folder'
            self._container = self.smart.Folders.get_folder(folder_id=container_id)
            self.container_path = f"{self.parent}/{self._container.name}"
        else:
            self.container_type = 'workspace'
            self._container = self.smart.Workspaces.get_workspace(workspace_id=container_id)
            self.container_path = self._container.name
        self.name: str = self._container.name
        self.id: int = self._container.id
        # Sheets
        if hasattr(self._container, 'sheets'):
            self.sheets = self._container.sheets
        # Reports
        if hasattr(self._container, 'reports'):
            self.reports = self._container.reports
        # Dashboards
        if hasattr(self._container, 'sights'):
            self.sights = self._container.sights
        # Folders
        if hasattr(self._container, 'folders'):
            for fldr in self._container.folders:
                self.folders.append(fldr)

        self.audit_report: dict = {
            "container_id": container_id,
            "name": self.name,
            "container_type": self.container_type,
            "container_path": self.container_path,
            "sheets": [],
            "reports": [],
            "dashboards": [],
            "folders": []
        }

    def audit(self):
        """
        Orchestrates an audit of all SmartCollections (Sheets, Dashboards, Reports) in this
        SmartContainer and saves the results in the ``audit_report`` property.

        Cycles through any sub-folders of this SmartContainer, stores their audit results in ``audit_report`` too.
        """
        self.audit_sheets()
        self.audit_reports()
        self.audit_dashboards()
        self.audit_folders()

    def audit_sheets(self):
        """

        :return:
        """
        for s in tqdm(self.sheets, f"sheets in '{self.container_path}'"):
            sht = self.smart.Sheets.get_sheet(sheet_id=s.id, include='ownerInfo,crossSheetReferences')
            coltitles = [c.title for c in sht.columns]
            cross_sheet_ref_sheet_ids = set([x.source_sheet_id for x in sht.cross_sheet_references])
            cross_sheet_ref_sheet_names = [SHEET_NAME_MAP[x] for x in cross_sheet_ref_sheet_ids]

            if len(cross_sheet_ref_sheet_ids) == 0:
                cross_sheet_ref_sheet_names = None

            audit_result = {
                "id"                    : sht.id,
                "name"                  : sht.name,
                "owner"                 : sht.owner,
                "cross_sheet_references": cross_sheet_ref_sheet_names,
                "created_at"            : sht.created_at.isoformat(),
                "modified_at"           : sht.modified_at.isoformat(),
                "permalink"             : sht.permalink,
                "total_row_count"       : sht.total_row_count,
                "column_titles"         : coltitles
            }
            self.audit_report['sheets'].append(audit_result)

    def audit_reports(self):
        for r in tqdm(self.reports, f"reports in '{self.container_path}'"):
            rpt = self.smart.Reports.get_report(report_id=r.id, include='ownerInfo,crossSheetReferences')
            coltitles = [c.title for c in rpt.columns]

            source_sheet_names = [s.name for s in rpt.source_sheets]

            # if len(cross_sheet_ref_sheet_ids)==0:
            #     cross_sheet_ref_sheet_names = None

            audit_result = {
                "id"             : rpt.id,
                "name"           : rpt.name,
                "owner"          : rpt.owner,
                "source_sheets"  : source_sheet_names,
                "created_at"     : rpt.created_at.isoformat(),
                "modified_at"    : rpt.modified_at.isoformat(),
                "permalink"      : rpt.permalink,
                "total_row_count": rpt.total_row_count,
                "column_titles"  : coltitles
            }
            self.audit_report['reports'].append(audit_result)

    def audit_dashboards(self):
        for d in tqdm(self.sights, f"dashboards in '{self.container_path}'"):
            dash = self.smart.Sights.get_sight(sight_id=d.id)
            widget_titles = []
            widget_source_sheet_ids = set()
            widget_source_sheet_names = []
            # analyse widgets
            for w in dash.widgets:
                if hasattr(w, 'title'):
                    widget_titles.append(w.title)
                if hasattr(w.contents, 'sheetId'):
                    widget_source_sheet_ids.add(w.contents.sheetId)
            if len(widget_source_sheet_ids) > 0:
                for sid in widget_source_sheet_ids:
                    widget_source_sheet_names.append(SHEET_NAME_MAP.get(sid))

            audit_result = {
                "id"                  : dash.id,
                "name"                : dash.name,
                "widget_source_sheets": widget_source_sheet_names,
                "created_at"          : dash.created_at.isoformat(),
                "modified_at"         : dash.modified_at.isoformat(),
                "permalink"           : dash.permalink,
                "widget_count"        : len(dash.widgets),
                "widget_titles"       : widget_titles
            }
            self.audit_report['dashboards'].append(audit_result)

    def audit_folders(self):
        for f in self.folders:
            fldr = SmartContainer(container_id=f.id, parent=self.container_path)
            f = fldr
            f.audit()
            self.audit_report['folders'].append(f.audit_report)

    def save_audit_to_smartsheets(self):
        """
        Future development: Save the audit report up to a dedicated (or specified) Smartsheet
        """
        pass


if __name__ == '__main__':
    sma = SmartsheetAudit()
