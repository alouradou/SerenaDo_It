import os
from datetime import datetime

from flask import Flask, request, render_template, url_for, send_file, abort
from flask_caching import Cache

from werkzeug.utils import secure_filename

from src.data_manager import DataManager, compute_timetable_header, StudentDataManager
from src.calendar_manager import CalendarManager
from src.exel_manager import ExcelManager
from src.parse_excel_line import ParseExcelLine
import src.personalize_timetable as personalize_timetable

cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
cache_duration = 60 * 60  # in seconds

app = Flask(__name__)
cache.init_app(app)

current_dir = os.path.abspath(os.path.dirname(__file__))
app.template_folder = os.path.join(current_dir, '../frontend/templates')
app.static_folder = os.path.join(current_dir, '../static')
app.config['UPLOAD_FOLDER'] = './uploads'

app.config['DEFAULT_SHEET_ID'] = "177HfBhAUT8XCkrVt-CFY1vD6mMOi-iFU3FKyUxIw7k8"
app.config['DEFAULT_SHEET_NAME'] = "année"
app.config['DEFAULT_STUDENT_SHEET_ID'] = "1KU6nJ8KGYOp4EH21jKKVwzF3vBDa8mDBaHFoaekx1ZU"
app.config['DEFAULT_STUDENT_SHEET_NAME'] = "effectif"


from src.api_admin import fetch_courses, admin_view


@app.route("/")
def hello_world():
    return render_template('index.html')


@app.route("/annee", methods=['GET'])
@cache.cached(timeout=cache_duration, query_string=True)
def get_event_list():
    custom_path = ""
    if request.args.get('sheet_id') and request.args.get('sheet_name'):
        sheet_id = request.args.get('sheet_id')
        sheet_name = request.args.get('sheet_name')
        custom_path = f"-{secure_filename(sheet_id)}-{secure_filename(sheet_name)}"
    else:
        sheet_id = app.config['DEFAULT_SHEET_ID']
        sheet_name = app.config['DEFAULT_SHEET_NAME']
    df = cache.get(f"df{custom_path}")
    if df is None:
        data_manager = DataManager(sheet_id, sheet_name=sheet_name)

        df = data_manager.excel_to_dataframe(sheet_name)
        df = compute_timetable_header(df)

        cache.set(f"df{custom_path}", df, timeout=cache_duration)

    list_week_start_dates = df["Semaine,du"].iloc[2:].dropna().drop_duplicates()

    course_list = []
    for week_date in list_week_start_dates:
        line_parser = ParseExcelLine(df, week_date)
        line_parser.parse()
        course_list += line_parser.course_list
    cache.set('course_list', course_list, timeout=cache_duration)

    cal = CalendarManager(course_list)
    cal.browse_course_list()

    path = f'year-calendar{custom_path}.ics'
    cal.save_calendar(os.path.join(app.config['UPLOAD_FOLDER'], path))

    return render_template('event-list.html',
                           course_list=course_list,
                           path="/ics?path=" + path,
                           host=request.host_url.split("//")[1][:-1],
                           displayed_name="Général")


@app.route("/eleves", methods=['GET'])
def get_student_list():
    student_sheet_id = app.config['DEFAULT_STUDENT_SHEET_ID']
    student_sheet_name = app.config['DEFAULT_STUDENT_SHEET_NAME']

    student_dm = StudentDataManager(student_sheet_id, student_sheet_name,
                                    saved_workbook_path="./uploads/tmp_students.xlsx",)

    student_df = student_dm.excel_to_dataframe(student_sheet_name)

    return render_template('student-list.html', student_df=student_df)


@app.route("/eleves/calendrier", methods=['GET'])
def get_student_calendar_from_list():
    student_id = int(request.args.get('id'))

    sheet_id, sheet_name = app.config['DEFAULT_SHEET_ID'], app.config['DEFAULT_SHEET_NAME']
    student_sheet_id = app.config['DEFAULT_STUDENT_SHEET_ID']
    student_sheet_name = app.config['DEFAULT_STUDENT_SHEET_NAME']

    # Chargement des étudiants
    student_dm = StudentDataManager(student_sheet_id, student_sheet_name,
                                    saved_workbook_path="./uploads/tmp_students.xlsx")
    students_df = student_dm.excel_to_dataframe(student_sheet_name)

    # Chargement de l'emploi du temps
    planning_dm = DataManager(sheet_id, sheet_name,
                              saved_workbook_path="./uploads/tmp_edt.xlsx")
    planning_dm.load_workbook()
    timetable = personalize_timetable.PersonalizeTimetable(
        "./uploads/tmp_edt.xlsx", sheet_name,
        "./uploads/tmp_students.xlsx", student_sheet_name)

    student = students_df.loc[students_df.index == student_id].iloc[0]
    custom_path = f"{secure_filename(student['prénom'])}-{secure_filename(student['nom'])}"
    filename = f"./uploads/edt-{custom_path}.xlsx"

    timetable.create_timetable_automatic(student["nom"], student["prénom"], filename)

    data_manager = ExcelManager(filename, sheet_name)

    df = data_manager.excel_to_dataframe(sheet_name)
    df = compute_timetable_header(df)

    list_week_start_dates = df["Semaine,du"].iloc[2:].dropna()

    course_list = []
    for week_date in list_week_start_dates:
        line_parser = ParseExcelLine(df, week_date)
        line_parser.parse()
        course_list += line_parser.course_list
    cal = CalendarManager(course_list)
    cal.browse_course_list()

    path = f'year-calendar-{custom_path}.ics'
    cal.save_calendar(os.path.join(app.config['UPLOAD_FOLDER'], path))

    if cache.get('course_list'):
        full_calendar_course_list = cache.get('course_list')
    else:
        get_event_list()
        full_calendar_course_list = cache.get('course_list')

    custom_full_course_path = f"-{secure_filename(sheet_id)}-{secure_filename(sheet_name)}"

    full_course_path = f'year-calendar{custom_full_course_path}.ics'
    cal.save_calendar(os.path.join(app.config['UPLOAD_FOLDER'], full_course_path))

    return render_template('event-list.html',
                           course_list=course_list,
                           full_course_list=full_calendar_course_list,
                           path="/ics?path=" + path,
                           full_course_path="/ics?path=" + full_course_path,
                           host=request.host_url.split("//")[1][:-1],
                           displayed_name=f"{student['prénom']} {student['nom']}")


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

        excel_manager = ExcelManager(os.path.join(app.config['UPLOAD_FOLDER'], filename),
                                     app.config['DEFAULT_SHEET_NAME'])
        df = excel_manager.excel_to_dataframe(app.config['DEFAULT_SHEET_NAME'])
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
                               displayed_name=file.filename)

    return abort(400, "No file uploaded")


# TODO: check vulnerabilities
@app.route("/ics", methods=['GET'])
def get_ics_calendar_from_file():
    # Validation du paramètre 'path'
    path = request.args.get('path')
    if not path:
        abort(400, "Le paramètre 'path' est manquant.")

    # Sécurisation du chemin du fichier
    safe_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(path))

    # Vérification de l'existence du fichier
    if not os.path.isfile(safe_path):
        abort(404, "Fichier non trouvé.")

    # Construire l'URL du site en utilisant url_for
    site_url = request.host_url

    # Construire l'URL complète avec le chemin vers la route
    full_url = url_for('get_ics_calendar_from_file', path=safe_path, _external=True)

    # Définir le MIME type comme 'text/calendar'
    mimetype = 'text/calendar'

    # Ajouter le lien 'webcal' et 'S'abonner'
    response = send_file(f"../uploads/{secure_filename(path)}", mimetype=mimetype, as_attachment=True)
    response.headers['Content-Disposition'] = 'attachment;filename=calendar.ics'
    response.headers['Link'] = f'<{site_url}webcal{full_url}>; rel=preload; as=script'

    return response


@app.route("/last-calendar")
def calendar():
    with open('./static/test-2024-01-15.ics', 'r') as f:
        return f.read()
