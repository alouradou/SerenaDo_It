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


@app.route("/admin")
def admin_view():
    categories = fetch_courses()
    print(categories)
    return render_template('admin.html',
                           categories=categories)


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
            print("Nouveau cours ajouté avec succès !")
        except sqlite3.Error as e:
            print("Erreur lors de l'ajout du nouveau cours dans la base de données :", e)
        finally:
            conn.close()

        return redirect(url_for('admin_view'))


