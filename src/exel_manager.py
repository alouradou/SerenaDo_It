import pandas as pd
import openpyxl
from openpyxl.cell import MergedCell
import requests

from src.data_manager import parse_merged_cell


# TODO: Test this class
class ExcelManager:
    def __init__(self, path, sheet_name=""):
        self.sheet_name = sheet_name
        self.xlsx_path = ""
        self.workbook = self.load_workbook()

    def load_workbook(self):
        file = requests.get(self.xlsx_path, allow_redirects=True)
        with open('tmp_workbook.xlsx', 'wb') as f:
            try:
                f.write(file.content)
                return openpyxl.load_workbook("./tmp_workbook.xlsx")
            except Exception as e:
                raise Exception(f"Error loading workbook from {self.xlsx_path}: {e}")

    def excel_to_dataframe(self, sheet_name, start_row=1):
        try:
            sheet = self.workbook[sheet_name]
        except KeyError:
            raise KeyError(f"Sheet '{sheet_name}' not found in the workbook.")

        data = []
        for row_idx, row in enumerate(sheet.iter_rows(min_row=start_row, values_only=True), start=start_row):
            parsed_row = [parse_merged_cell(sheet, row_idx, col_idx + 1) for col_idx, value in enumerate(row)]
            data.append(parsed_row)

        return pd.DataFrame(data)