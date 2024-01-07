import re


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
            self.description = cell_content_parts[0]
            self.location = "Salle " + cell_content_parts[-1].strip()
            match = re.search(r'\((.*?)\)', cell_content_parts[-2] if len(cell_content_parts) > 1 else "")
            self.organizer = match.group(1) if match else None
        except IndexError:
            self.description = cell_content_parts[0]
