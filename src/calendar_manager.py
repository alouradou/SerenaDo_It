from datetime import datetime, timedelta
from icalendar import Calendar, Event


class CalendarManager:
    def __init__(self, course_list):
        self.course_list = course_list
        self.cal = Calendar()  # Initialisez votre calendrier ici

    def create_event(self, start_datetime, end_datetime, summary, location, speaker):
        event = Event()
        event.add('summary', summary)
        event.add('dtstart', start_datetime)
        event.add('dtend', end_datetime)
        event.add('location', location)
        event.add('description', speaker)
        self.cal.add_component(event)

    def browse_course_list(self):
        for course in self.course_list:
            self.create_event(course.start, course.end, course.description, course.location, course.organizer)

    def save_calendar(self, file_path):
        with open(file_path, 'wb') as f:
            f.write(self.cal.to_ical())

# Exemple d'utilisation
# calendar_manager = CalendarManager()
# calendar_manager.create_event(start_datetime, end_datetime, "Titre de l'événement")
# calendar_manager.save_calendar('mon_calendrier.ics')
