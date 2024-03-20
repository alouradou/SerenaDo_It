from flask import redirect

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


def fetch_unknown_courses():
    conn = sqlite3.connect('./uploads/serenadoit.db')
    cursor = conn.cursor()

    unknown_courses = []
    try:
        cursor.execute("SELECT course_name FROM unknown_courses")
        rows = cursor.fetchall()
        for row in rows:
            print(row[0])
            unknown_courses.append(row[0])
    except sqlite3.Error as e:
        print("Erreur lors de la récupération des données depuis la base de données :", e)
    finally:
        conn.close()

    return unknown_courses


@app.route("/admin")
def admin_view():
    categories = fetch_courses()
    unknown_courses = fetch_unknown_courses()
    return render_template('admin.html',
                           categories=categories,
                           unknown_courses=unknown_courses)


@app.route("/admin/delete_course", methods=['POST'])
def delete_course():
    if request.method == 'POST':
        course = request.form.get('course')
        denomination = request.form.get('denomination')

        conn = sqlite3.connect('./uploads/serenadoit.db')
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM courses WHERE course_name = ? AND alias = ?", (course, denomination))
            conn.commit()
            print("Cours supprimé avec succès !")
        except sqlite3.Error as e:
            print("Erreur lors de la suppression du cours depuis la base de données :", e)
        finally:
            conn.close()

        return redirect(url_for('admin_view'))


@app.route("/admin/add_course", methods=['POST'])
def add_course():
    if request.method == 'POST':
        course = request.form.get('course')
        denomination = request.form.get('denomination')

        conn = sqlite3.connect('./uploads/serenadoit.db')
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO courses (course_name, alias) VALUES (?, ?)", (course, denomination))
            conn.commit()
            print("Nouveau cours ajouté avec succès !", course, denomination)
            cursor.execute("DELETE FROM unknown_courses WHERE course_name = ?", (denomination,))
            conn.commit()
            print("Cours supprimé de la liste des cours inconnus avec succès !", denomination)
        except sqlite3.Error as e:
            print("Erreur lors de l'ajout du nouveau cours dans la base de données :", e)
        finally:
            conn.close()

        return redirect(url_for('admin_view'))


