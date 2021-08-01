import json
import logging
import os
from pprint import pprint
import requests
from envparse import env
from tqdm import tqdm
import smartsheet


SHEET_NAME_MAP = {}



class SmartSheetAudit:
    """
    Audit runner - this is the class used to run a Smartsheets audit.

    Uses environment variables for API key and local filepaths, instantiates sheets and boards objects

    .. code-block:: python
       :caption: Usage
       :name: SmartSheetAudit-usage

       app = SmartSheetAudit()
       app.run()
    """

    def __init__(self):
        env.read_envfile('smartsheets.env')
        self.sheets = Sheets()
        self.boards = Dashboards()
        self.reports = Reports()

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

class Sheets:
    """Collection of Sheet sheet objects

    `Smartsheets API documentation: sheets <https://smartsheet.redoc.ly/tag/sheets#operation/list-sheets>`_
    """
    def __init__(self):
        global SHEET_NAME_MAP
        self.sheets = []         # list of smartsheets
        self.getsheetid = {}     # dict key is sheet name, value is sheet_id
        self.getsheetname = {}   # dict key is sheet_id, value is sheet name
        self.sheet_details = []
        self.url = "https://api.smartsheet.com/2.0/sheets"
        self.headers = {f"Authorization": f"Bearer {env('SMARTSHEET_ACCESS_TOKEN')}", }

    def api_get_sheets(self):
        # List all Smartsheets the API can see
        # Currently doesn't handle multiple pages returned
        # ListMySheets
        # GET https://api.smartsheet.com/2.0/sheets
        try:
            response = requests.get(url=self.url,
                                    params={"include": "ownerInfo"},
                                    headers=self.headers)
            # print('Response HTTP Status Code: {status_code}'.format(status_code=response.status_code))
            j = response.json()
            with open(f'{env("JSON_FOLDER")}/smartsheets.json', 'w') as f:
                json.dump(j, f)
            self.sheets = j['data']
        except requests.exceptions.RequestException:
            print('HTTP Request failed')

    def api_get_sheet(self, sheetid:int):
        j = None
        try:
            response = requests.get(url=f"{self.url}/{sheetid}",
                                    params={"include": "crossSheetReferences"},
                                    headers=self.headers)
            j = response.json()
        except requests.exceptions.RequestException:
            print('HTTP Request failed')
        if j:
            return j

    def create_sheet_maps(self):
        # pprint(self.sheets)
        global SHEET_NAME_MAP
        for sheet in self.sheets:
            self.getsheetid[sheet['name']] = sheet['id']
            self.getsheetname[sheet['id']] = sheet['name']
        SHEET_NAME_MAP = self.getsheetname

    def save_sheets_audit(self, filename):
        print("auditing sheets ...")
        if filename:
            # could be fancier about this - bottom line we're saving a pipe delimited file in the text files folder
            # this doesn't do any error checking (like validity of name/type
            filepath = f"{env('TEXT_FOLDER')}/{filename}"
            audit_file_header = f"id|name|owner|workspace|crossSheetReferences|" \
                                f"createdAt|modifiedAt|permalink|rowCount|columnTitles"
            # print(audit_file_header)
            with open(filepath, 'w') as writer:
                writer.write(f"{audit_file_header}\n")
                for s in tqdm(self.sheets):
                    ssht = Sheet()
                    ssht.id = s.get('id')
                    ssht.api_get_details()
                    ssht.process_api_data()
                    writer.write(f"{ssht.audit_items()}\n")
                    # print(this_ssht.audit_items())
                print(f"audit data saved to {filepath} ({len(self.sheets)} records)")


class Sheet:
    """Individual Sheet sheet containing all the details from the GET sheets/sheet_id call to the API

    `Smartsheets API documentation : sheet <https://smartsheet.redoc.ly/tag/sheets#operation/getSheet>`_
    """
    def __init__(self):
        global SHEET_NAME_MAP
        self.url = "https://api.smartsheet.com/2.0/sheets"
        self.headers = {f"Authorization": f"Bearer {env('SMARTSHEET_ACCESS_TOKEN')}", }
        self.api_data = {}
        self.id = None
        self.name = None
        self.xsrefs = set([])
        self.workspace = {}
        self.crossSheetReferences = None
        self.owner = None
        self.columns = None
        self.createdAt = None
        self.modifiedAt = None
        self.permalink = None
        self.totalRowCount = None


    def api_get_details(self):
        j = None
        try:
            response = requests.get(url=f"{self.url}/{self.id}",
                                    params={"include": "crossSheetReferences,ownerInfo", },
                                    headers=self.headers)
            j = response.json()
        except requests.exceptions.RequestException:
            print('HTTP Request failed')
        if j:
            self.api_data = j
            self.process_api_data()

    def process_api_data(self):
        for k, v in self.api_data.items():
            self.__setattr__(k, v)
        if self.crossSheetReferences:
            for xsref in self.crossSheetReferences:
                xsr_id = xsref.get('sourceSheetId')
                self.xsrefs.add(xsr_id)

    def audit_items(self):
        global SHEET_NAME_MAP
        xsreflist = [SHEET_NAME_MAP[x] for x in self.xsrefs]
        coltitles = [c.get('title') for c in self.columns]
        deets = f"{self.id}|{self.name}|{self.owner}|{self.workspace.get('name')}|" \
                f"{xsreflist}|{self.createdAt}|{self.modifiedAt}|" \
                f"{self.permalink}|{self.totalRowCount}|{coltitles}"
        return deets


class Dashboards:
    """Collection of Sheet dashboard objects visible to this API key

    `Smartsheets API documentation: dashboards (sights) <https://smartsheet.redoc.ly/tag/dashboards#operation/list-sights>`_
    """

    def __init__(self):
        env.read_envfile('smartsheets.env')
        self.smart = smartsheet.Smartsheet()
        response = self.smart.Sights.list_sights(include_all=True)
        self.boards = response.data

        self.url = "https://api.smartsheet.com/2.0/sights"
        self.headers = {f"Authorization": f"Bearer {env('SMARTSHEET_ACCESS_TOKEN')}", }
        self.boards = []

    def print_list(self):
        pprint([(b.id, b.name) for b in self.boards])

    def api_get_boards(self):
        try:
            response = requests.get(url=self.url,
                                    headers=self.headers)
            j = response.json()
            with open(f'{env("JSON_FOLDER")}/dashboards.json', 'w') as f:
                json.dump(j, f)
            self.boards = j['data']
        except requests.exceptions.RequestException:
            print('HTTP Request failed')

    def save_boards_audit(self, filename):
        print("\nauditing dashboards ...\n")
        if filename:
            filepath = f"{env('TEXT_FOLDER')}/{filename}"
            audit_file_header = "id|name|workspace|sheetReferences|" \
                                "createdAt|modifiedAt|permalink|" \
                                "widgetCount|widgetTitles"

            with open(filepath, 'w') as writer:
                writer.write(f"{audit_file_header}\n")
                for s in tqdm(self.boards):
                    this_board = Dashboard()
                    this_board.id = s.get('id')
                    this_board.api_get_details()
                    writer.write(f"{this_board.audit_items()}\n")

                print(f"\naudit data saved to {filepath} ({len(self.boards)} records)")



class Dashboard:
    """Details for a single Smartsheets Dashboard

    `Smartsheets API documentation: dashboard (sight) <https://smartsheet.redoc.ly/tag/dashboards#operation/get-sight>`_
    """

    def __init__(self):
        self.url = "https://api.smartsheet.com/2.0/sights"
        self.headers = {f"Authorization": f"Bearer {env('SMARTSHEET_ACCESS_TOKEN')}", }
        self.widgets = {}
        self.widget_count = 0
        self.widget_titles = []
        self.widget_sheets = set()
        self.widget_sheet_names = []
        self.api_data = {}
        self.workspace = {}

    def api_get_details(self):
        j = None
        try:
            response = requests.get(url=f"{self.url}/{self.id}",
                                    headers=self.headers)
            j = response.json()
        except requests.exceptions.RequestException:
            print('HTTP Request failed')
        if j:
            self.api_data = j
            self.process_api_data()

    def process_api_data(self):
        """set all of the key/value pairs of the api data extract as attributes of this class"""
        for k, v in self.api_data.items():
            self.__setattr__(k, v)
        self.widget_count = len(self.widgets)
        self.analyse_widgets()

    def analyse_widgets(self):
        for w in self.widgets:
            if w.get('title'):
                self.widget_titles.append(w.get('title'))
            if w.get('contents',{}).get('sheetId'):
                self.widget_sheets.add(w.get('contents',{}).get('sheetId'))
        for sid in self.widget_sheets:
            self.widget_sheet_names.append(SHEET_NAME_MAP.get(sid))

    def audit_items(self):
        """returns the data items which appear in the audit report
        could do with renaming"""
        deets = f"{self.id}|{self.name}|{self.workspace.get('name')}|{self.widget_sheet_names}|" \
                f"{self.createdAt}|{self.modifiedAt}|{self.permalink}|" \
                f"{self.widget_count}|{self.widget_titles}"
        return deets


class Reports:
    """Collection of Report objects"""

    def __init__(self):
        env.read_envfile('smartsheets.env')
        self.smart = smartsheet.Smartsheet()
        response = self.smart.Reports.list_reports(include_all=True)
        self.reports = response.data

    @property
    def listing(self):
        return [(r.id, r.name) for r in self.reports]



    def save_reports_audit(self, filename):
        print("\nauditing reports ...\n")
        filepath = f"{env('TEXT_FOLDER')}/{filename}"
        report_audit_header = (
        'id', 'name', 'workspace', 'sourceSheets', 'createdAt', 'modifiedAt', 'permalink', 'rowCount', 'columnTitles')

        with open(filepath, 'w') as writer:
            writer.write(f"{'|'.join(report_audit_header)}\n")
            for r in tqdm(self.reports):
                rpt = Report(r.id)
                writer.write(f"{rpt.audit_items()}\n")

            print(f"\naudit data saved to {filepath} ({len(self.reports)} records)")


class Report():
    """Individual Smartsheets report object"""

    def __init__(self, report_id):
        env.read_envfile('smartsheets.env')
        self.smart = smartsheet.Smartsheet()
        response = self.smart.Reports.get_report(report_id=report_id, include='sourceSheets')
        self.report = response

    def audit_items(self):
        """list of items which will appear on a row of the audit report"""
        deets = f"{self.report.id}|" \
                f"{self.report.name}|" \
                f"{self.report.workspace.name if self.report.workspace else None}|" \
                f"{[s.name for s in self.report.source_sheets]}|" \
                f"{self.report.created_at}|" \
                f"{self.report.modified_at}|" \
                f"{self.report.permalink}|" \
                f"{self.report.total_row_count}|" \
                f"{[c.title for c in self.report.columns]}"
        return deets


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

    def __init__(self, parent=""):
        self.parent: str = ''
        self.container_type: str = ''
        self.container_path: str = ''
        # container_path = parent / name
        self.audit_report: dict = {}

    def audit(self):
        """
        Orchestrates an audit of all SmartCollections (Sheets, Dashboards, Reports) in this
        SmartContainer and saves the results in the ``audit_report`` property
        """
        pass

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
    # app = SmartSheetAudit()
    # app.run()
    rpts = Reports()
    pprint(rpts.listing)