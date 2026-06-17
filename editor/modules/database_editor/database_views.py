import pygame

from editor.modules.database_editor.database_widgets import (
    draw_database_field,
    draw_database_picklist_dropdown,
)
from editor.modules.database_editor.database_theme import (
    ACCENT,
    BORDER,
    CARD,
    CARD_ACTIVE,
    INNER_PANEL,
    MUTED,
    TEXT,
    WARNING,
)


class CategoryNavigator:
    def __init__(self):
        self.buttons = []

    def handle_click(self, pos):
        for button in self.buttons:
            if button["rect"].collidepoint(pos):
                return button["category_id"]

        return None

    def draw(self, screen, rect, categories, selected_category_id, font_label, font_body):
        x = rect.x
        y = rect.y + 28
        width = rect.width
        row_height = 42
        self.buttons = []

        heading = font_body.render("Categorias", True, MUTED)
        screen.blit(heading, (x, rect.y))

        for index, category in enumerate(categories):
            row = pygame.Rect(x, y + index * (row_height + 8), width, row_height)
            color = CARD_ACTIVE if category.id == selected_category_id else CARD
            pygame.draw.rect(screen, color, row, border_radius=5)
            pygame.draw.rect(screen, BORDER, row, 1, border_radius=5)

            marker = pygame.Rect(row.x + 12, row.y + 11, 6, 20)
            marker_color = ACCENT if category.is_active() else MUTED
            pygame.draw.rect(screen, marker_color, marker, border_radius=2)

            label = font_label.render(category.label, True, TEXT)
            screen.blit(
                label,
                (
                    row.x + 30,
                    row.y + (row.height - label.get_height()) // 2,
                ),
            )

            if category.planned:
                tag = font_body.render("planned", True, MUTED)
                screen.blit(
                    tag,
                    (
                        row.right - tag.get_width() - 14,
                        row.y + (row.height - tag.get_height()) // 2,
                    ),
                )

            self.buttons.append({
                "rect": row,
                "category_id": category.id,
            })


class MasterDetailView:
    def __init__(self):
        self.selected_record_id = None
        self.record_buttons = []
        self.list_scroll_y = 0
        self.list_max_scroll = 0
        self.detail_scroll_y = 0
        self.detail_max_scroll = 0
        self.list_rect = None
        self.detail_rect = None
        self.field_buttons = []
        self.dropdown_buttons = []
        self.dropdown_request = None

    def ensure_selection(self, records):
        record_ids = [record.id for record in records]

        if self.selected_record_id not in record_ids:
            self.selected_record_id = record_ids[0] if record_ids else None

    def handle_click(self, pos):
        for button in self.record_buttons:
            if button["rect"].collidepoint(pos):
                self.selected_record_id = button["record_id"]
                self.detail_scroll_y = 0
                return {
                    "type": "record",
                    "record_id": self.selected_record_id,
                }

        for button in self.field_buttons:
            if button["rect"].collidepoint(pos):
                action = dict(button["action"])
                action["record_id"] = self.selected_record_id
                return action

        for button in self.dropdown_buttons:
            if button["rect"].collidepoint(pos):
                return button["action"]

        return None

    def handle_scroll(self, pos, amount):
        if self.detail_rect and self.detail_rect.collidepoint(pos):
            self.detail_scroll_y = clamp_scroll(
                self.detail_scroll_y,
                amount,
                self.detail_max_scroll,
            )
            return True

        self.list_scroll_y = clamp_scroll(
            self.list_scroll_y,
            amount,
            self.list_max_scroll,
        )
        return True

    def draw(self, screen, rect, title, records, font_label, font_body, edit_state=None, dropdown_state=None):
        self.ensure_selection(records)

        title_text = font_label.render(title, True, TEXT)
        screen.blit(title_text, (rect.x, rect.y))

        count_text = font_body.render(
            f"{len(records)} definiciones cargadas",
            True,
            MUTED,
        )
        screen.blit(count_text, (rect.x, rect.y + 28))

        list_width = max(320, int(rect.width * 0.42))
        list_rect = pygame.Rect(rect.x, rect.y + 62, list_width, rect.height - 62)
        detail_rect = pygame.Rect(
            list_rect.right + 18,
            rect.y + 62,
            rect.width - list_width - 18,
            rect.height - 62,
        )
        self.list_rect = list_rect
        self.detail_rect = detail_rect

        self.draw_list(screen, list_rect, records, font_label, font_body)
        self.draw_detail(screen, detail_rect, records, font_label, font_body, edit_state, dropdown_state)

    def draw_list(self, screen, list_rect, records, font_label, font_body):
        pygame.draw.rect(screen, INNER_PANEL, list_rect, border_radius=5)
        pygame.draw.rect(screen, BORDER, list_rect, 1, border_radius=5)

        row_height = 58
        content_height = len(records) * row_height
        self.list_max_scroll = max(0, content_height - list_rect.height + 12)
        self.list_scroll_y = min(self.list_scroll_y, self.list_max_scroll)
        self.record_buttons = []

        previous_clip = screen.get_clip()
        screen.set_clip(list_rect)

        y = list_rect.y + 8 - self.list_scroll_y

        for record in records:
            row = pygame.Rect(list_rect.x + 8, y, list_rect.width - 16, row_height - 8)

            if row.bottom >= list_rect.y and row.y <= list_rect.bottom:
                self.draw_record_row(screen, row, record, font_label, font_body)
                self.record_buttons.append({
                    "rect": row,
                    "record_id": record.id,
                })

            y += row_height

        screen.set_clip(previous_clip)
        draw_scrollbar(screen, list_rect, self.list_scroll_y, self.list_max_scroll)

    def draw_record_row(self, screen, row, record, font_label, font_body):
        color = CARD_ACTIVE if record.id == self.selected_record_id else CARD
        pygame.draw.rect(screen, color, row, border_radius=5)
        pygame.draw.rect(screen, BORDER, row, 1, border_radius=5)

        title = font_label.render(record.title, True, TEXT)
        screen.blit(title, (row.x + 12, row.y + 7))

        detail_text = font_body.render("   ".join(record.summary_parts), True, MUTED)
        screen.blit(detail_text, (row.x + 12, row.y + 31))

        if record.flags.get("missing_sprite"):
            no_sprite = font_body.render("no sprite", True, WARNING)
            screen.blit(no_sprite, (row.right - no_sprite.get_width() - 12, row.y + 8))

        if record.flags.get("dirty"):
            dirty = font_body.render("modified", True, WARNING)
            screen.blit(dirty, (row.right - dirty.get_width() - 12, row.y + 31))

    def draw_detail(self, screen, detail_rect, records, font_label, font_body, edit_state=None, dropdown_state=None):
        pygame.draw.rect(screen, INNER_PANEL, detail_rect, border_radius=5)
        pygame.draw.rect(screen, BORDER, detail_rect, 1, border_radius=5)

        record = get_record_by_id(records, self.selected_record_id)
        if record is None:
            message = font_body.render("No hay registros disponibles.", True, MUTED)
            screen.blit(message, (detail_rect.x + 16, detail_rect.y + 16))
            return

        rows = record.detail_rows
        line_height = 30
        section_gap = 8
        content_height = 48

        for row in rows:
            content_height += section_gap if row["type"] == "section" else line_height
            content_height += line_height

        self.detail_max_scroll = max(0, content_height - detail_rect.height + 24)
        self.detail_scroll_y = min(self.detail_scroll_y, self.detail_max_scroll)

        previous_clip = screen.get_clip()
        screen.set_clip(detail_rect)
        self.field_buttons = []
        self.dropdown_buttons = []
        self.dropdown_request = None

        y = detail_rect.y + 16 - self.detail_scroll_y
        x = detail_rect.x + 16
        width = detail_rect.width - 32
        row_width = max(220, width - 12)

        title = font_label.render(record.id, True, TEXT)
        screen.blit(title, (x, y))
        y += 32

        for row in rows:
            if row["type"] == "section":
                y += section_gap
                section_text = font_label.render(row["label"], True, ACCENT)
                if y + section_text.get_height() >= detail_rect.y and y <= detail_rect.bottom:
                    screen.blit(section_text, (x, y))
                y += line_height
                continue

            if y + line_height >= detail_rect.y and y <= detail_rect.bottom:
                field_button = draw_database_field(
                    screen,
                    pygame.Rect(x, y - 2, row_width, line_height + 4),
                    row,
                    edit_state,
                    record.id,
                    dropdown_state,
                )

                if row.get("editable"):
                    self.field_buttons.append({
                        "rect": field_button["rect"],
                        "action": field_button["action"],
                    })

                if field_button.get("dropdown_request"):
                    self.dropdown_request = field_button["dropdown_request"]

            y += line_height

        screen.set_clip(previous_clip)
        if self.dropdown_request is not None:
            self.dropdown_buttons = draw_database_picklist_dropdown(
                screen,
                self.dropdown_request,
            )
        draw_scrollbar(screen, detail_rect, self.detail_scroll_y, self.detail_max_scroll)

def draw_scrollbar(screen, rect, scroll_y, max_scroll):
    if max_scroll <= 0:
        return

    track = pygame.Rect(rect.right - 8, rect.y + 6, 4, rect.height - 12)
    pygame.draw.rect(screen, (54, 59, 68), track, border_radius=2)

    visible_ratio = rect.height / (rect.height + max_scroll)
    thumb_height = max(32, int(track.height * visible_ratio))
    max_thumb_y = track.height - thumb_height
    thumb_y = track.y + int(max_thumb_y * (scroll_y / max_scroll))
    thumb = pygame.Rect(track.x, thumb_y, track.width, thumb_height)
    pygame.draw.rect(screen, ACCENT, thumb, border_radius=2)


def clamp_scroll(current, amount, max_scroll):
    return max(0, min(current + amount, max_scroll))


def get_record_by_id(records, record_id):
    for record in records:
        if record.id == record_id:
            return record

    return None

