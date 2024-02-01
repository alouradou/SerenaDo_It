from src.api_flask import *


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
