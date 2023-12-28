class Course:
    def __init__(self):
        self.description = ""
        self.start = None
        self.end = None

    def __str__(self):
        return f"Course: {self.description} ({self.start} - {self.end})"
