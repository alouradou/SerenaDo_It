from datetime import datetime, timedelta
import pandas as pd

from src.course import Course


jours_vers_chiffres = {
    "Lundi": 0,
    "Mardi": 1,
    "Mercredi": 2,
    "Jeudi": 3,
    "Vendredi": 4,
    "Samedi": 5,
    "Dimanche": 6
}


def select_week_from_date(df, date):
    try:
        col_from = pd.to_datetime(df["Semaine,du"], format="%Y-%m-%d", errors='coerce')
        col_to = pd.to_datetime(df["Semaine,au"], format="%Y-%m-%d", errors='coerce')

        selected_row = df.loc[(col_from <= date) & (date - timedelta(days=2) <= col_to)]

        return selected_row
    except TypeError as e:
        print(e)
        return pd.DataFrame()


def get_date_from_day_of_week(week_start_date, day_of_week):
    try:
        return week_start_date + timedelta(days=jours_vers_chiffres[day_of_week.strip()])
    except KeyError as e:
        print(e)
        return None


# Transforms a string like "8h" or "8h30" into a time object
def translate_to_time(time_str):
    time_format = "%Hh%M"

    if time_str.endswith('h'):
        time_str = time_str + '00'

    translated_time = datetime.strptime(time_str, time_format).time()

    return translated_time


def is_course_continuation(previous, current):
    if (previous.cell_content == current.cell_content
            and (current.start - previous.end <= timedelta(minutes=30))):
        return True
    else:
        return False


class ParseExcelLine:
    def __init__(self, df: pd.DataFrame, date: datetime):
        line = select_week_from_date(df, date)

        self.line = line
        self.week_start_date = line["Semaine,du"].values[0]
        self.current_course = Course()
        self.previous_course = Course()
        self.course_list = []

    def parse(self):
        for col in self.line:
            self.current_course = Course()
            self.current_course.cell_content = self.line[col].values[0]
            self.current_course.get_description()

            # Splitting the header to get the day of the week and the time
            split = str(col).split(",")

            try:
                week_day = split[0]
                time = split[1].split("-")

                start_time = translate_to_time(time[0])
                end_time = translate_to_time(time[1])

                date = get_date_from_day_of_week(self.week_start_date, week_day)

                print(date, self.week_start_date, week_day, time, start_time, end_time)

                # Merge date and time
                self.current_course.start = datetime.combine(date, start_time)
                self.current_course.end = datetime.combine(date, end_time)

                # If the course is a continuation of the previous one, merge them
                if is_course_continuation(self.previous_course, self.current_course):
                    self.current_course.start = self.previous_course.start
                # Base case: Add only if there is a course to memorize
                elif self.previous_course.cell_content:
                    self.course_list.append(self.previous_course)

                self.previous_course = self.current_course

            except IndexError:
                continue
            except ValueError as e:
                if (("time data 'du' does not match format '%Hh%M'" in str(e)) or
                        ("time data 'au' does not match format '%Hh%M'" in str(e))):
                    continue
                else:
                    raise e

        # Border case: Add the last course if not None
        if self.previous_course.cell_content:
            self.course_list.append(self.previous_course)
