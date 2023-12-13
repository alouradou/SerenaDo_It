class MainApp:
    def __init__(self, data_path):
        self.data_manager = DataManager(data_path)
        self.calendar_manager = CalendarManager()

    def process_events(self):
        for row_index in range(len(self.data_manager.data)):
            event_data = self.data_manager.get_event_data(row_index)
            # Effectuez votre logique de traitement des événements ici
            start_datetime, end_datetime = self.process_event_data(event_data)
            summary = event_data['VotreColonneDeTitre']
            self.calendar_manager.create_event(start_datetime, end_datetime, summary)

    def process_event_data(self, event_data):
        # Implémentez votre logique de traitement des données d'événement ici
        pass

    def save_calendar(self, file_path):
        self.calendar_manager.save_calendar(file_path)

# Exemple d'utilisation
# app = MainApp('votre_fichier.csv')
# app.process_events()
# app.save_calendar('mon_calendrier.ics')
