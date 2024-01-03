import os
from datetime import datetime

import requests
from flask import Flask, request, render_template, url_for, send_file
from flask_caching import Cache

from werkzeug.utils import secure_filename

from src.data_manager import DataManager, compute_timetable_header
from src.calendar_manager import CalendarManager
from src.exel_manager import ExcelManager
from src.github_files_manager import GithubFilesManager
from src.parse_excel_line import ParseExcelLine

cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
cache_duration = 60 * 60  # in seconds

app = Flask(__name__)
cache.init_app(app)

current_dir = os.path.abspath(os.path.dirname(__file__))
app.template_folder = os.path.join(current_dir, '../frontend/templates')
app.static_folder = os.path.join(current_dir, '../static')
app.config['UPLOAD_FOLDER'] = './uploads'


@app.route("/")
def hello_world():
    return render_template('index.html')


@app.route("/annee")
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

    cal = CalendarManager(course_list)
    cal.browse_course_list()

    path = f'year-calendar.ics'
    cal.save_calendar(os.path.join(app.config['UPLOAD_FOLDER'], path))

    return render_template('event-list.html',
                           course_list=course_list,
                           path="/ics?path=" + path,
                           host=request.host_url.split("//")[1][:-1],
                           filename="Général")


@app.route("/eleves")
def get_student_list():
    gh = GithubFilesManager()
    file_dict = gh.get_github_files()
    print(file_dict)
    return render_template('auto-fetch.html', file_list=file_dict)


@app.route("/eleves/lien", methods=['GET'])
def get_student_custom_calendar():
    args = request.args
    path = args.get('path')

    response = requests.get(path)

    if response.status_code == 200:
        filename = secure_filename(path.split("/")[-1])
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'wb') as f:
            f.write(response.content)

        excel_manager = ExcelManager(os.path.join(app.config['UPLOAD_FOLDER'], filename), ***REMOVED***)
        df = excel_manager.excel_to_dataframe(***REMOVED***)
        df = compute_timetable_header(df)

        list_week_start_dates = df["Semaine,du"].iloc[2:].dropna()

        course_list = []
        for week_date in list_week_start_dates:
            line_parser = ParseExcelLine(df, week_date)
            line_parser.parse()
            course_list += line_parser.course_list
        cache.set('course_list_' + filename, course_list, timeout=cache_duration)

        cal = CalendarManager(course_list)
        cal.browse_course_list()

        path = f'{filename}.ics'
        cal.save_calendar(os.path.join(app.config['UPLOAD_FOLDER'], path))

        return render_template('event-list.html',
                               course_list=course_list,
                               path="/ics?path=" + path,
                               host=request.host_url.split("//")[1][:-1],
                               filename=path.split("/")[-1])

    return 'No file uploaded'


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
    cal.save_calendar(os.path.join(app.config['UPLOAD_FOLDER'], path))

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


@app.route('/annee/source-excel', methods=['POST'])
def upload_xlsx():
    if 'file' in request.files:
        file = request.files['file']
        filename = secure_filename(file.filename)
        # see https://stackabuse.com/step-by-step-guide-to-file-upload-with-flask/
        print(f"Saving file to: {os.path.join(app.config['UPLOAD_FOLDER'], filename)}")
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
            print(f"File saved successfully: {os.path.join(app.config['UPLOAD_FOLDER'], filename)}")
        else:
            print(f"Error saving file: {os.path.join(app.config['UPLOAD_FOLDER'], filename)}")

        excel_manager = ExcelManager(os.path.join(app.config['UPLOAD_FOLDER'], filename), ***REMOVED***)
        df = excel_manager.excel_to_dataframe(***REMOVED***)
        df = compute_timetable_header(df)

        list_week_start_dates = df["Semaine,du"].iloc[2:].dropna()

        course_list = []
        for week_date in list_week_start_dates:
            line_parser = ParseExcelLine(df, week_date)
            line_parser.parse()
            course_list += line_parser.course_list
        cache.set('course_list_' + filename, course_list, timeout=cache_duration)

        cal = CalendarManager(course_list)
        cal.browse_course_list()

        path = f'{filename}.ics'
        cal.save_calendar("./static/" + path)

        return render_template('event-list.html',
                               course_list=course_list,
                               path="/ics?path=" + path,
                               host=request.host_url.split("//")[1][:-1],
                               filename=file.filename)

    return 'No file uploaded'


# TODO: check vulnerabilities
@app.route("/ics", methods=['GET'])
def get_ics_calendar_from_file():
    args = request.args
    path = "../static/" + args.get('path')

    # Construire l'URL du site en utilisant url_for
    site_url = request.host_url  # Cela récupère le domaine du site, y compris le protocole (http/https)

    # Construire l'URL complète avec le chemin vers la route
    full_url = url_for('get_ics_calendar_from_file', path=args.get('path'), _external=True)

    # Définir le MIME type comme 'text/calendar'
    mimetype = 'text/calendar'

    # Ajouter le lien 'webcal' et 'S'abonner'
    response = send_file(path, mimetype=mimetype, as_attachment=True)
    response.headers['Content-Disposition'] = 'attachment;filename=calendar.ics'
    response.headers['Link'] = f'<{site_url}webcal{full_url}>; rel=preload; as=script'

    return response


@app.route("/last-calendar")
def calendar():
    with open('./static/test-2024-01-15.ics', 'r') as f:
        return f.read()

