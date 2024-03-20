import re


def get_location_string(cell_string):
    try:
        return "Salle " + str(int(cell_string))
    except ValueError:
        match = re.match(r'([(]?salle\s*)?(\d+)[)]?', cell_string, re.IGNORECASE)
    if match:
        return "Salle " + match.group(2)
    else:
        return cell_string


def get_organizer_string(cell_string):
    cell_string = cell_string.strip()
    match = re.search(r'^\((.*?)\)$', cell_string)
    if match:
        return match.group(1)
    else:
        return cell_string


class Course:
    def __init__(self):
        self.cell_content = ""
        self.description = ""
        self.location = ""
        self.organizer = ""
        self.start = None
        self.end = None

    def __str__(self):
        return f"Course: {self.description} ({self.start} - {self.end})"

    def get_description(self):
        cell_content_parts = str(self.cell_content).split("\n")
        try:
            self.description = cell_content_parts[0].strip()
            self.location = get_location_string(cell_content_parts[-1])
            self.organizer = get_organizer_string(cell_content_parts[-2]) if len(cell_content_parts) > 1 else ""
        except IndexError:
            self.description = cell_content_parts[0]
