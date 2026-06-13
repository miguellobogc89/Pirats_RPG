from dataclasses import dataclass, field

from game.cartography.expedition_setup import ExpeditionSetup


@dataclass
class CartographyUIState:
    selected_region_id: str | None = None
    modal_open: bool = False
    pending_expedition_region_id: str | None = None
    expedition_setup: ExpeditionSetup | None = None
    region_cells: dict = field(default_factory=dict)
    expedition_button: object | None = None
    cancel_button: object | None = None
    launch_button: object | None = None

    def clear_hitboxes(self):
        self.region_cells.clear()
        self.expedition_button = None
        self.cancel_button = None
        self.launch_button = None
