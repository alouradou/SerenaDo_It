import unittest

from src.course import Course


class TestCourse(unittest.TestCase):
    def test_course(self):
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
