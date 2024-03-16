import unittest

from src.course import Course
from src.personalize_timetable import detect_matching


class TestCourse(unittest.TestCase):
    def test_fill_cal_fields(self):
        course = Course()
        course.cell_content = """TC1 : Agilité
(Oresys)
217"""
        course.get_description()

        self.assertEqual(course.description, "TC1 : Agilité")
        self.assertEqual(course.location, "Salle 217")
        self.assertEqual(course.organizer, "Oresys")

        course.cell_content = """conf  "product manager"
Intervenant (Entreprise) 
salle 218"""

        course.get_description()

        self.assertEqual(course.description, 'conf  "product manager"')
        self.assertEqual(course.location, "Salle 218")
        self.assertEqual(course.organizer, "Intervenant (Entreprise)")

        course.cell_content = """Cybersécurité
Intervenant
(salle  218)"""

        course.get_description()

        self.assertEqual(course.description, 'Cybersécurité')
        self.assertEqual(course.location, "Salle 218")
        self.assertEqual(course.organizer, "Intervenant")

    def test_detect_matching(self):
        class Cell:
            def __init__(self, value: str):
                self.value = value

        cell = Cell("réseaux\nIntervenant\nsalle 218")
        deleted_courses = ["réseaux"]
        self.assertTrue(detect_matching(cell, deleted_courses))

        deleted_courses = ["écosystème digital"]

        cell = Cell("Eco-système digital")
        self.assertTrue(detect_matching(cell, deleted_courses))

        cell = Cell("eco-système digital")
        self.assertTrue(detect_matching(cell, deleted_courses))

        cell = Cell("écosystème digital")
        self.assertTrue(detect_matching(cell, deleted_courses))

        cell = Cell("économie")
        self.assertFalse(detect_matching(cell, deleted_courses))
