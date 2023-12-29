import os
from datetime import datetime

from flask import Flask, request, render_template
from flask_caching import Cache

from src.data_manager import DataManager, compute_timetable_header
from src.calendar_manager import CalendarManager
from src.parse_excel_line import ParseExcelLine


cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})

app = Flask(__name__)
cache.init_app(app)


current_dir = os.path.abspath(os.path.dirname(__file__))
app.template_folder = os.path.join(current_dir, '../frontend/templates')


@app.route("/")
def hello_world():
    return render_template('index.html')


@app.route("/event-list")
@cache.cached(timeout=60)
def get_event_list():
    # Chemin vers le fichier de données (dans l'url google sheets)
    sheet_id = ***REMOVED***

    data_manager = DataManager(sheet_id, sheet_name=***REMOVED***)

    df = data_manager.excel_to_dataframe(***REMOVED***)
    df = compute_timetable_header(df)

    list_week_start_dates = df["Semaine,du"].iloc[2:].dropna()

    course_list = []
    for week_date in list_week_start_dates:
        line_parser = ParseExcelLine(df, week_date)
        line_parser.parse()
        course_list += line_parser.course_list
    cache.set('course_list', course_list, timeout=60)
    return render_template('event-list.html', course_list=course_list)


@app.route("/year-calendar")
def get_calendar():
    # Call course list route first to cache the course list
    get_event_list()
    course_list = cache.get('course_list')
    cal = CalendarManager(course_list)
    cal.browse_course_list()

    date = datetime.now()
    path = f'year-calendar.ics'
    cal.save_calendar("./static/"+path)

    return render_template('calendar.html', path="/ics?path="+path)


# TODO: check vulnerabilities
@app.route("/ics", methods=['GET'])
def get_ics_calendar_from_file():
    args = request.args
    path = "./static/"+args.get('path')
    with open(path, 'r') as f:
        return f.read()


@app.route("/last-calendar")
def calendar():
    with open('./static/test-2024-01-15.ics', 'r') as f:
        return f.read()




if __name__ == "__main__":
    app.run(debug=True)
