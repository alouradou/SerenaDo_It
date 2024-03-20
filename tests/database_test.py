import os
import unittest

import sqlite3

os.chdir('..')


class TestDatabase(unittest.TestCase):
    def test_db_connection(self):
        conn = sqlite3.connect('./uploads/serenadoit.db')
        self.assertTrue(conn)
        conn.close()

    def test_fetch_courses(self):
        conn = sqlite3.connect('./uploads/serenadoit.db')
        cursor = conn.cursor()

        table_exists = False

        categories = {}
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='courses'")
            table_exists = cursor.fetchone()
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

        self.assertTrue(table_exists)
        self.assertTrue(categories)

    def test_fetch_unknown_courses(self):
        conn = sqlite3.connect('./uploads/serenadoit.db')
        cursor = conn.cursor()

        table_exists = False

        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='unknown_courses'")
            table_exists = cursor.fetchone()
        except sqlite3.Error as e:
            print("Erreur lors de la récupération des données depuis la base de données :", e)
        finally:
            conn.close()

        self.assertTrue(table_exists)
