import os

from flask import Flask, render_template

from src.data_manager import DataManager, compute_timetable_header
from src.calendar_manager import CalendarManager
from src.parse_excel_line import ParseExcelLine

app = Flask(__name__)

current_dir = os.path.abspath(os.path.dirname(__file__))
app.template_folder = os.path.join(current_dir, '../frontend/templates')


@app.route("/")
def hello_world():
    return render_template('index.html')


@app.route("/get-event-list")
def get_event_list():
    # Chemin vers le fichier de données (dans l'url google sheets)
    sheet_id = ***REMOVED***

    data_manager = DataManager(sheet_id, sheet_name=***REMOVED***)

    df = data_manager.excel_to_dataframe(***REMOVED***)
    df = compute_timetable_header(df)

    list_week_start_dates = df["Semaine,du"].iloc[2:].dropna()

    course_list = []
    for week_date in list_week_start_dates:
        print(week_date)
        line_parser = ParseExcelLine(df, week_date)
        line_parser.parse()
        course_list += line_parser.course_list
    return render_template('event-list.html', course_list=course_list)


@app.route("/last-calendar")
def calendar():
    with open('./static/test-2024-01-15.ics', 'r') as f:
        return f.read()


if __name__ == "__main__":
    app.run(debug=True)
