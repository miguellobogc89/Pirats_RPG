from dataclasses import dataclass, field

from game.cartography.expedition_setup import ExpeditionSetup


@dataclass
class CartographyUIState:
    selected_region_id: str | None = None
    modal_open: bool = False
    reward_modal_open: bool = False
    pending_expedition_region_id: str | None = None
    expedition_setup: ExpeditionSetup | None = None
    region_cells: dict = field(default_factory=dict)
    inventory_transfer_buttons: list = field(default_factory=list)
    storage_transfer_buttons: list = field(default_factory=list)
    expedition_button: object | None = None
    rewards_button: object | None = None
    cancel_button: object | None = None
    launch_button: object | None = None
    rewards_close_button: object | None = None

    def clear_hitboxes(self):
        self.region_cells.clear()
        self.inventory_transfer_buttons.clear()
        self.storage_transfer_buttons.clear()
        self.expedition_button = None
        self.rewards_button = None
        self.cancel_button = None
        self.launch_button = None
        self.rewards_close_button = None
