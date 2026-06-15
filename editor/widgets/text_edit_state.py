import pygame


class TextEditState:
    def __init__(self):
        self.text = ""
        self.cursor = 0
        self.selection_anchor = None

    def set_text(self, text):
        self.text = str(text)
        self.cursor = len(self.text)
        self.selection_anchor = None

    def has_selection(self):
        return self.selection_anchor is not None and self.selection_anchor != self.cursor

    def get_selection_range(self):
        if not self.has_selection():
            return self.cursor, self.cursor

        return (
            min(self.selection_anchor, self.cursor),
            max(self.selection_anchor, self.cursor),
        )

    def select_all(self):
        self.selection_anchor = 0
        self.cursor = len(self.text)

    def clear_selection(self):
        self.selection_anchor = None

    def replace_selection(self, value):
        start, end = self.get_selection_range()
        self.text = self.text[:start] + value + self.text[end:]
        self.cursor = start + len(value)
        self.clear_selection()

    def selected_text(self):
        start, end = self.get_selection_range()
        return self.text[start:end]

    def move_cursor(self, amount, selecting=False, word=False):
        if word:
            new_cursor = self.find_word_boundary(amount)
        else:
            new_cursor = max(0, min(len(self.text), self.cursor + amount))

        if selecting and self.selection_anchor is None:
            self.selection_anchor = self.cursor

        self.cursor = new_cursor

        if not selecting:
            self.clear_selection()

    def find_word_boundary(self, direction):
        if direction < 0:
            index = self.cursor
            while index > 0 and self.text[index - 1].isspace():
                index -= 1
            while index > 0 and not self.text[index - 1].isspace():
                index -= 1
            return index

        index = self.cursor
        while index < len(self.text) and not self.text[index].isspace():
            index += 1
        while index < len(self.text) and self.text[index].isspace():
            index += 1
        return index

    def backspace(self):
        if self.has_selection():
            self.replace_selection("")
            return

        if self.cursor <= 0:
            return

        self.text = self.text[: self.cursor - 1] + self.text[self.cursor :]
        self.cursor -= 1

    def delete(self):
        if self.has_selection():
            self.replace_selection("")
            return

        if self.cursor >= len(self.text):
            return

        self.text = self.text[: self.cursor] + self.text[self.cursor + 1 :]

    def insert_text(self, value, max_length=None):
        if max_length is not None:
            available = max(0, max_length - (len(self.text) - len(self.selected_text())))
            value = value[:available]

        if value:
            self.replace_selection(value)


def init_clipboard():
    try:
        if not pygame.scrap.get_init():
            pygame.scrap.init()
        return True
    except pygame.error:
        return False


def copy_to_clipboard(text):
    if not init_clipboard():
        return False

    pygame.scrap.put(pygame.SCRAP_TEXT, text.encode("utf-8"))
    return True


def paste_from_clipboard():
    if not init_clipboard():
        return ""

    data = pygame.scrap.get(pygame.SCRAP_TEXT)

    if not data:
        return ""

    return data.decode("utf-8", errors="ignore").replace("\x00", "")
