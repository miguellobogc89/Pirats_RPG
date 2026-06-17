class TextEditState:
    def __init__(self):
        self.active_id = None
        self.text = ""
        self.cursor_index = 0
        self.selection_range = None

    def start(self, field_id, text):
        self.active_id = field_id
        self.text = str(text)
        self.cursor_index = len(self.text)
        self.selection_range = None

    def stop(self):
        self.active_id = None
        self.text = ""
        self.cursor_index = 0
        self.selection_range = None

    def is_active(self, field_id):
        return self.active_id == field_id

    def insert_text(self, value):
        value = str(value)
        self.text = self.text[:self.cursor_index] + value + self.text[self.cursor_index:]
        self.cursor_index += len(value)

    def backspace(self):
        if self.cursor_index <= 0:
            return

        self.text = self.text[:self.cursor_index - 1] + self.text[self.cursor_index:]
        self.cursor_index -= 1