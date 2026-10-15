"""One-time manual QA fixture: fill free inventory slots without replacing items."""
from game.inventory.inventory_manager import get_inventory_grid
from game.inventory.item_transactions import receive, quantity

FILLER_ITEMS = (
    "amethyst", "apple", "black_pearl", "carrot", "citrine",
    "coal", "compass", "coral_fragment", "driftwood", "egg",
    "emerald", "gold", "iron", "meat", "ruby", "sapphire",
    "silver", "copper_ore", "gold_ore", "iron_ore",
)


def fill_inventory_for_crafting_test(state):
    """Preserve existing stacks and add different items until every slot is occupied."""
    if state.get("crafting_inventory_full_test_granted"):
        return
    grid = get_inventory_grid(state)
    for item_id in FILLER_ITEMS:
        if not any(slot is None for row in grid for slot in row):
            break
        if quantity(state, item_id) == 0:
            receive(state, item_id, 1)
    if not any(slot is None for row in grid for slot in row):
        state["crafting_inventory_full_test_granted"] = True
