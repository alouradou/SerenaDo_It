from datetime import datetime, timedelta
import pandas as pd

from src.data_manager import DataManager
from src.calendar_manager import CalendarManager
from src.app import MainApp
from src.parse_excel_line import ParseExcelLine





def main():
    # Chemin vers le fichier de données (dans l'url google sheets)
    sheet_id = ***REMOVED***

    data_manager = DataManager(sheet_id, sheet_name=***REMOVED***)

    df = data_manager.excel_to_dataframe(***REMOVED***)

    date = datetime(2024, 1, 15)

    line_parser = ParseExcelLine(df, date)
    line_parser.parse()

    cal = CalendarManager(line_parser.course_list)
    cal.browse_course_list()

    cal.save_calendar(f'test-{date.strftime("%Y-%m-%d")}.ics')


if __name__ == "__main__":
    main()
