from dataclasses import dataclass


@dataclass
class SlotReference:
    container_id: str
    index: int


@dataclass
class SlotUIState:
    hovered_slot: SlotReference | None = None
    selected_slot: SlotReference | None = None
    drag_origin: SlotReference | None = None
    dragged_stack: dict | None = None
    is_dragging: bool = False

    def clear_hover(self):
        self.hovered_slot = None

    def clear_selection(self):
        self.selected_slot = None

    def start_drag(self, origin, stack):
        self.drag_origin = origin
        self.dragged_stack = copy_stack(stack)
        self.is_dragging = self.dragged_stack is not None

    def cancel_drag(self):
        self.drag_origin = None
        self.dragged_stack = None
        self.is_dragging = False

    def clear(self):
        self.clear_hover()
        self.clear_selection()
        self.cancel_drag()


def copy_stack(stack):
    if stack is None:
        return None

    return {
        "item_id": stack["item_id"],
        "amount": stack["amount"],
    }
