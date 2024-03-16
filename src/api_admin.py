from src.api_flask import *

import sqlite3


def fetch_courses():
    conn = sqlite3.connect('./uploads/serenadoit.db')
    cursor = conn.cursor()

    categories = {}
    try:
        cursor.execute("SELECT course_name, alias FROM courses")
        rows = cursor.fetchall()
        for row in rows:
            category, name = row
            if category in categories:
                categories[category].append(name)
            else:
                categories[category] = [name]
    except sqlite3.Error as e:
        print("Erreur lors de la récupération des données depuis la base de données :", e)
    finally:
        conn.close()

    return categories


@app.route("/admin")
def admin_view():
    categories = fetch_courses()
    print(categories)
    return render_template('admin.html',
                           categories=categories)
