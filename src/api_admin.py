import requests
from flask import redirect, flash

from src.api_flask import *

import sqlite3


def fetch_config():
    conn = sqlite3.connect('./uploads/serenadoit.db')
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT sheet_id, sheet_name, student_sheet_id, student_sheet_name FROM sheets ORDER BY date DESC")
        rows = cursor.fetchall()
        if len(rows) > 0:
            sheet_id, sheet_name, student_sheet_id, student_sheet_name = rows[0]
            return sheet_id, sheet_name, student_sheet_id, student_sheet_name
        else:
            return None
    except sqlite3.Error as e:
        print("Erreur lors de la récupération des données depuis la base de données :", e)
    finally:
        conn.close()

    return None


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
    error = request.args.get('error')
    categories = fetch_courses()
    unknown_courses = fetch_unknown_courses()
    return render_template('admin.html',
                           categories=categories,
                           unknown_courses=unknown_courses,
                           error=error)


@app.route("/admin/personalize_sheet", methods=['POST'])
def personalize_sheet():
    # store sheet_id, sheet_name, student_sheet_id, student_sheet_name
    if request.method == 'POST':
        sheet_id = request.form.get('sheet_id')
        sheet_name = request.form.get('sheet_name')
        student_sheet_id = request.form.get('student_sheet_id')
        student_sheet_name = request.form.get('student_sheet_name')

        try:
            sheet_response = requests.get(f'https://docs.google.com/spreadsheets/d/{sheet_id}')
            student_sheet_response = requests.get(f'https://docs.google.com/spreadsheets/d/{student_sheet_id}')

            if sheet_response.status_code == 200 and student_sheet_response.status_code == 200:
                # store in db
                conn = sqlite3.connect('./uploads/serenadoit.db')
                cursor = conn.cursor()

                try:
                    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute("INSERT INTO sheets (sheet_id, sheet_name, "
                                   "student_sheet_id, student_sheet_name, date) "
                                   "VALUES (?, ?, ?, ?, ?)",
                                   (sheet_id, sheet_name, student_sheet_id, student_sheet_name, date))
                    conn.commit()
                    print("Sheets added successfully !")
                except sqlite3.Error as e:
                    print("Error while adding sheets to the database :", e)
                    return redirect(url_for('admin_view',
                                            error='Erreur lors de l\'ajout des configurations à la base de données.'))
                finally:
                    conn.close()
            else:
                print('Failed to access one or more of the Google Sheets. Please check the IDs and try again.')
                return redirect(url_for('admin_view',
                                        error='Au moins Google Sheet est inaccessible. '
                                              'Veuillez vérifier les identifiants et réessayer.'))

        except requests.exceptions.RequestException as e:
            flash('An error occurred while trying to access the Google Sheets.', 'error')
            return redirect(url_for('admin_view',
                                    error='Une erreur est survenue lors de l\'accès aux Google Sheets.'))

        return redirect(url_for('admin_view'))


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
