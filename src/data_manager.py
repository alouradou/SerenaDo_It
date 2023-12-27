import pandas as pd
import openpyxl
from openpyxl.cell import MergedCell
import requests


def parse_merged_cell(sheet, row, col):
    cell = sheet.cell(row=row, column=col)
    if isinstance(cell, MergedCell):
        for merged_range in sheet.merged_cells.ranges:
            if cell.coordinate in merged_range:
                # return the left top cell
                cell = sheet.cell(row=merged_range.min_row, column=merged_range.min_col)
                break
    return cell.value


class DataManager:
    def __init__(self, sheet_id, sheet_name=""):
        self.sheet_name = sheet_name
        # https://stackoverflow.com/questions/33713084/download-link-for-google-spreadsheets-csv-export-with-multiple-sheets
        self.csv_url = "https://docs.google.com/spreadsheets/d/"+sheet_id+"/gviz/tq?tqx=out:csv&sheet="+sheet_name
        self.xlsx_url = "https://docs.google.com/spreadsheets/d/"+sheet_id+"/export?format=xlsx&id="+sheet_id
        self.workbook = self.load_workbook()

    def load_workbook(self):
        file = requests.get(self.xlsx_url, allow_redirects=True)
        with open('tmp_workbook.xlsx', 'wb') as f:
            try:
                f.write(file.content)
                return openpyxl.load_workbook("./tmp_workbook.xlsx")
            except Exception as e:
                raise Exception(f"Error loading workbook from {self.xlsx_url}: {e}")

    def get_from_csv(self):
        return pd.read_csv(self.csv_url)

    def excel_to_dataframe(self, sheet_name, start_row=1):
        try:
            sheet = self.workbook[sheet_name]
        except KeyError:
            raise KeyError(f"Sheet '{sheet_name}' not found in the workbook.")

        data = []
        for row_idx, row in enumerate(sheet.iter_rows(min_row=start_row, values_only=True), start=start_row):
            parsed_row = [parse_merged_cell(sheet, row_idx, col_idx + 1) for col_idx, value in enumerate(row)]
            data.append(parsed_row)

        headers = data[0]
        df = pd.DataFrame(data[1:], columns=headers)
        return df


# Exemple d'utilisation
# data_manager = DataManager('id_du_fichier')
# event_data = data_manager.get_event_data(0)
