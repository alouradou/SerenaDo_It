import os
import unittest
import openpyxl
from openpyxl.styles import Alignment, Font, Border, Side

from src.create_timetable import CreateTimetable


class TestCreateTimetable(unittest.TestCase):

    def setUp(self):
        # Créer une instance de CreateTimetable avec des fichiers de test
        self.timetable = CreateTimetable(
            edt_file_name='../uploads/edt Do_It.23-24.xlsx',
            edt_sheet_name='année',
            students_file_name='../uploads/tmp.xlsx',
            students_sheet_name='effectif'
        )
        # Initialiser la feuille 2 avec des données de test
        self.timetable.sheet2.append(['Test', 'Test'] + ['X'] * self.timetable.sheet2.max_column)

    def test_create_timetable_automatic(self):
        # Appeler la méthode avec l'étudiant de test
        self.timetable.create_timetable_automatic('Test', 'Test', '../uploads/test_output.xlsx')

        # Charger la feuille de calcul d'origine et la feuille générée par le test
        original_workbook = openpyxl.load_workbook('../uploads/edt Do_It.23-24.xlsx')
        generated_workbook = openpyxl.load_workbook('../uploads/test_output.xlsx')

        # Vérifier que le fichier a été créé
        self.assertTrue(generated_workbook)

        # Vérifier que chaque cours présent dans la feuille générée était sélectionné par l'étudiant Test Test
        for row in range(1, original_workbook.active.max_row + 1):
            for col in range(1, original_workbook.active.max_column + 1):
                original_cell = original_workbook.active.cell(row=row, column=col).value
                generated_cell = generated_workbook.active.cell(row=row, column=col).value
                # print(f'Comparing cell at ({row}, {col})')
                # print(original_cell)
                if original_cell is not None:
                    msg = (f'\n\nCell at ({row}, {col}) does not match.\n\n'
                           f'Original:\n{original_cell}\n\n'
                           f'Generated:\n{generated_cell}\n')
                    self.assertEqual(original_cell, generated_cell, msg)


def tearDown(self):
        # Supprimer les fichiers de test après chaque test
        files_to_remove = ['test_edt.xlsx', 'test_etudiants.xlsx', 'test_output.xlsx']
        for file_name in files_to_remove:
            try:
                os.remove(file_name)
            except FileNotFoundError:
                pass


if __name__ == '__main__':
    unittest.main()
