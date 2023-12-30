import os
from datetime import datetime

from flask import Flask, request, render_template
from flask_caching import Cache

from src.data_manager import DataManager, compute_timetable_header
from src.calendar_manager import CalendarManager
from src.exel_manager import ExcelManager
from src.parse_excel_line import ParseExcelLine

cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
cache_duration = 60 * 60  # in seconds

app = Flask(__name__)
cache.init_app(app)

current_dir = os.path.abspath(os.path.dirname(__file__))
app.template_folder = os.path.join(current_dir, '../frontend/templates')
app.static_folder = os.path.join(current_dir, '../static')
app.config['UPLOAD_FOLDER'] = '../static/uploads'


@app.route("/")
def hello_world():
    return render_template('index.html')


@app.route("/event-list")
@cache.cached(timeout=cache_duration)
def get_event_list():
    df = cache.get('df')
    if not df:
        # Chemin vers le fichier de données (dans l'url google sheets)
        sheet_id = ***REMOVED***

        data_manager = DataManager(sheet_id, sheet_name=***REMOVED***)

        df = data_manager.excel_to_dataframe(***REMOVED***)
        df = compute_timetable_header(df)

        cache.set('df', df, timeout=cache_duration)

    list_week_start_dates = df["Semaine,du"].iloc[2:].dropna()

    course_list = []
    for week_date in list_week_start_dates:
        line_parser = ParseExcelLine(df, week_date)
        line_parser.parse()
        course_list += line_parser.course_list
    cache.set('course_list', course_list, timeout=cache_duration)
    return render_template('event-list.html', course_list=course_list)


@app.route("/year-calendar")
def get_calendar():
    # Call course list route first to cache the course list
    course_list = cache.get('course_list')
    if not course_list:
        get_event_list()
        course_list = cache.get('course_list')
    cal = CalendarManager(course_list)
    cal.browse_course_list()

    date = datetime.now()
    path = f'year-calendar.ics'
    cal.save_calendar("./static/" + path)

    return render_template('calendar.html', path="/ics?path=" + path)


@app.route("/my-calendar")
def get_personalization_menu():
    course_list = cache.get('course_list')
    if not course_list:
        get_event_list()
        course_list = cache.get('course_list')
    desc = [course_list[i].description for i in range(len(course_list))]
    print(desc)
    unique_desc = list(set(desc))
    return render_template('personalize.html', selectable_courses=unique_desc, course_list=course_list)


@app.route('/upload', methods=['POST'])
def upload_xlsx():
    if 'file' in request.files:
        file = request.files['file']
        # filename = secure_filename(file.filename) : see https://stackabuse.com/step-by-step-guide-to-file-upload-with-flask/
        filename = file.filename
        print(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        excel_manager = ExcelManager(os.path.join(app.config['UPLOAD_FOLDER'], filename), ***REMOVED***)
        df = excel_manager.excel_to_dataframe(***REMOVED***)
        df = compute_timetable_header(df)

        return 'File uploaded successfully'+str(df)

    return 'No file uploaded'

# TODO: check vulnerabilities
@app.route("/ics", methods=['GET'])
def get_ics_calendar_from_file():
    args = request.args
    path = "./static/" + args.get('path')
    with open(path, 'r') as f:
        return f.read()


@app.route("/last-calendar")
def calendar():
    with open('./static/test-2024-01-15.ics', 'r') as f:
        return f.read()


if __name__ == "__main__":
    app.run(debug=True)
