class Course:
    def __init__(self):
        self.cell_content = ""
        self.description = ""
        self.start = None
        self.end = None

    def __str__(self):
        return f"Course: {self.description} ({self.start} - {self.end})"

    def get_description(self):
        self.description = str(self.cell_content).split("\n")[0]
