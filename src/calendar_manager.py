from datetime import datetime, timedelta
# from icalendar import Calendar, Event


class CalendarManager:
    def __init__(self):
        self.cal = None #Calendar()  # Initialisez votre calendrier ici

    def create_event(self, start_datetime, end_datetime, summary):
        event = None#Event()
        event.add('summary', summary)
        event.add('dtstart', start_datetime)
        event.add('dtend', end_datetime)
        self.cal.add_component(event)

    def save_calendar(self, file_path):
        with open(file_path, 'wb') as f:
            f.write(self.cal.to_ical())

# Exemple d'utilisation
# calendar_manager = CalendarManager()
# calendar_manager.create_event(start_datetime, end_datetime, "Titre de l'événement")
# calendar_manager.save_calendar('mon_calendrier.ics')
