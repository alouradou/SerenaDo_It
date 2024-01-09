from datetime import datetime, timedelta
import pandas as pd

from src.data_manager import DataManager
from src.calendar_manager import CalendarManager
from src.parse_excel_line import ParseExcelLine

import src.api_flask as api


def main():
    api.app.run(debug=True)


def generate_default_calendar():
    # Chemin vers le fichier de données (dans l'url google sheets)
    sheet_id = ""

    data_manager = DataManager(sheet_id, sheet_name="***REMOVED***")

    df = data_manager.excel_to_dataframe("***REMOVED***")

    list_week_start_dates = df["Semaine,du"].iloc[2:]

    course_list = []
    for week_date in list_week_start_dates:
        line_parser = ParseExcelLine(df, week_date)
        line_parser.parse()
        course_list += line_parser.course_list

    cal = CalendarManager(course_list)
    cal.browse_course_list()

    date = datetime.now()
    cal.save_calendar(f'./static/year-calendar-{date.strftime("%Y-%m-%d")}.ics')


if __name__ == "__main__":
    main()
