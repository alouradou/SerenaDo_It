from src.data_manager import DataManager
from src.calendar_manager import CalendarManager
from src.app import MainApp

def main():
    # Chemin vers votre fichier de données
    data_path = 'data/your_data.csv'

    # Initialisation des gestionnaires de données et de calendrier
    data_manager = DataManager(data_path,type='spreadsheet')
    calendar_manager = CalendarManager()

    # Initialisation de l'application principale
    app = MainApp(data_manager, calendar_manager)

    # Traitement des événements
    app.process_events()

    # Enregistrement du calendrier
    calendar_file_path = 'output/my_calendar.ics'
    app.save_calendar(calendar_file_path)

    print("Le fichier ICS a été créé avec succès.")

if __name__ == "__main__":
    main()
