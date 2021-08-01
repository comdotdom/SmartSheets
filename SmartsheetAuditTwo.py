import json
import logging
import os
from pprint import pprint
import requests
from envparse import env
from tqdm import tqdm
import smartsheet


SHEET_NAME_MAP = {}



class SmartsheetAudit:
    """
    **Audit runner** - this is the class used to run a Smartsheet audit.

    Uses environment variables for API key and local filepaths

    Instantiates SmartContainer (Workspace) objects to orchestrate their respective audits.

    **Usage**

    .. code-block:: python

       app = SmartSheetAudit()
       app.run()
    """
    def __init__(self):
        env.read_envfile('smartsheets.env')
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
        # self.sheets = Sheets()
        # self.boards = Dashboards()
        # self.reports = Reports()

    def run(self):
        """Runs the full audit process:

              #. Calls the API to get a  full listing of all the sheets visible to the API key owner
              #. Creates mappings dicts for sheet name/id lookup
              #. Audits each sheet and saves the results into a specified pipe delimited text file
              #. Calls the API to get a full listing of all the dashboards visible to the API key owner
              #. Audits them each in turn and saves the results to a specified pipe delimited text file

        .. todo:: Separately audit local objects (no workspace) and each individual workspace
        .. todo:: Dynamic file naming based on workspace
        """

        # Sheets
        self.sheets.api_get_sheets()
        self.sheets.create_sheet_maps()
        self.sheets.save_sheets_audit('ss_sheets_audit_test.txt')

        # Dashboards
        self.boards.api_get_boards()
        self.boards.save_boards_audit('ss_dashboards_audit_test.txt')

        # Reports
        self.reports.save_reports_audit('ss_reports_audit_test.txt')


class SmartContainer:
    """
    Workspaces and Folders can contain folders, sheets, dashboards and reports.

    SmartContainer is a base class which may be a Workspace or a Folder,
    but which provides the audit orchestration functionality required of a SmartCollection,
    and the audit_results property to store the results of the audit.

    A SmartContainer will have a ``container_path`` property which shows a breadcrumb trail
    of its own folder structure - starting at the ultimate parent Workspace.

    (Data Governance) Audits are actually carried out by SmartCollections (Sheets, Dashboards and Reports).
    The audit method of a SmartContainer calls the audit method of a SmartCollection,
    which returns the audit_results as a dict.
    """

    def __init__(self, container_id: int, parent: str = None):
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

        if hasattr(self._container, 'folders'):
            """needs bit of thinking - for loop creates a list of SmartContainers, from each child folder_id"""
            for fldr in self._container.folders:
                self.folders.append(SmartContainer(container_id=fldr.id, parent=self.container_path))

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
        SmartContainer and saves the results in the ``audit_report`` property
        """
        # SHEETS
        for s in tqdm(self.sheets, f"sheets in '{self.container_path}'"):
            sht = self.smart.Sheets.get_sheet(sheet_id=s.id, include='ownerInfo,crossSheetReferences')
            coltitles = [c.title for c in sht.columns]
            cross_sheet_ref_sheet_ids = set([x.source_sheet_id for x in sht.cross_sheet_references])
            cross_sheet_ref_sheet_names = [SHEET_NAME_MAP[x] for x in cross_sheet_ref_sheet_ids]

            if len(cross_sheet_ref_sheet_ids)==0:
                cross_sheet_ref_sheet_names = None

            audit_result = {
                "id": sht.id,
                "name": sht.name,
                "owner": sht.owner,
                "cross_sheet_references": cross_sheet_ref_sheet_names,
                "created_at": sht.created_at,
                "modified_at": sht.modified_at,
                "permalink": sht.permalink,
                "total_row_count":sht.total_row_count,
                "column_titles": coltitles
            }
            self.audit_report['sheets'].append(audit_result)
        # -------------------------------------------------------------------------------------------------------
        # REPORTS
        for r in tqdm(self.reports, f"reports in '{self.container_path}'"):
            rpt = self.smart.Reports.get_report(report_id=r.id, include='ownerInfo,crossSheetReferences')
            coltitles = [c.title for c in rpt.columns]

            source_sheet_names = [s.name for s in rpt.source_sheets]

            if len(cross_sheet_ref_sheet_ids)==0:
                cross_sheet_ref_sheet_names = None

            audit_result = {
                "id": rpt.id,
                "name": rpt.name,
                "owner": rpt.owner,
                "source_sheets": source_sheet_names,
                "created_at": rpt.created_at,
                "modified_at": rpt.modified_at,
                "permalink": rpt.permalink,
                "total_row_count":rpt.total_row_count,
                "column_titles": coltitles
            }
            self.audit_report['reports'].append(audit_result)
        # -------------------------------------------------------------------------------------------------------
        # DASHBOARDS
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
                "id"             : dash.id,
                "name"           : dash.name,
                "widget_source_sheets"  : widget_source_sheet_names,
                "created_at"     : dash.created_at,
                "modified_at"    : dash.modified_at,
                "permalink"      : dash.permalink,
                "widget_count":    len(dash.widgets),
                "widget_titles"  : widget_titles
            }

            self.audit_report['dashboards'].append(audit_result)
        # -------------------------------------------------------------------------------------------------------
        # FOLDERS
        for f in self.folders:
            fldr = SmartContainer(container_id=f.id, parent=self.container_path)
            f = fldr
            f.audit()
            self.audit_report['folders'].append(f.audit_report)
        # =======================================================================================================
        pprint(self.audit_report)

    def save_audit_to_smartsheets(self):
        """
        Future development: Save the audit report up to a dedicated (or specified) Smartsheet
        """
        pass


class SmartCollection:
    """
    Sheets, Dashboard and Reports are all examples of SmartCollections.

    They are the built by calling the Smartsheets API (via the SDK) and contain all the
    sheet, dashboard or report objects in scope.

    A SmartContainer will have its own SmartCollections for each of the three object types
    (as long as objects of that type exist in the container !)

    The audit method of a SmartCollection gathers specific facts about each object in the collection
    and builds up a dict for each object. It collects those dicts in a list.

    That list is the put into an audit_report dict which contains information about the SmartCollection itself,
    as well as all the audit reports.
    """

    def __init__(self):
        self.collection_type: str = ''
        self.container_path: str = ''
        self.audit_report: dict = {}

    def audit(self):
        """
        Carry out data governance audit of this SmartCollection's objects and store the results in ``audit_report``
        """
        pass


if __name__ == '__main__':
    sma = SmartsheetAudit()
