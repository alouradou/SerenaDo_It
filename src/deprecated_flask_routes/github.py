@app.route("/github")
def get_github_file_list():
    gh = GithubFilesManager()
    file_dict = gh.get_github_files()
    print(file_dict)
    return render_template('auto-fetch.html', file_list=file_dict)


@app.route("/github/calendrier", methods=['GET'])
def get_student_custom_calendar():
    args = request.args
    path = args.get('path')

    response = requests.get(path)

    if response.status_code == 200:
        filename = secure_filename(path.split("/")[-1])
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'wb') as f:
            f.write(response.content)

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
                               displayed_name=path.split("/")[-1])

    return abort(400, "Error fetching file")