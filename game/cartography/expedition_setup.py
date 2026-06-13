from dataclasses import dataclass, field


@dataclass
class ExpeditionSetup:
    region_id: str
    cost: dict
    travel_requirements: dict
    gold_required: int
    gold_available: int
    required_items: dict = field(default_factory=dict)
    assigned_items: dict = field(default_factory=dict)
    selected_cargo: list = field(default_factory=list)
    capacity_used: int = 0
    can_launch: bool = False
    validation_errors: list = field(default_factory=list)

    def get_assigned_resources(self):
        return {
            "gold": self.gold_required,
            "items": self.required_items.copy(),
        }


def create_expedition_setup(
    region_id,
    expedition_manager,
    ship_storage,
    state=None,
    selected_cargo=None,
):
    cost = expedition_manager.calculate_expedition_cost(region_id)
    validation_errors = []
    travel_requirements = {
        "gold": 0,
        "items": {},
        "crew": {},
        "ship_upgrades": [],
        "monsters": {},
    }

    if cost is None:
        cost = {}
        validation_errors.append("region_not_found")
    else:
        travel_requirements = cost["travel_requirements"]

    gold_required = travel_requirements["gold"]
    gold_available = 0

    if state is not None:
        gold_available = state.get("resources", {}).get("gold", 0)

    required_items = travel_requirements["items"].copy()
    assigned_items = {}

    if ship_storage is None:
        selected_cargo = [] if selected_cargo is None else selected_cargo
        capacity_used = calculate_capacity_used(selected_cargo)
        max_capacity = capacity_used
    else:
        if selected_cargo is None:
            selected_cargo = ship_storage.get_items_snapshot()

        for item_id in required_items:
            assigned_items[item_id] = ship_storage.get_item_amount(item_id)

        capacity_used = ship_storage.get_used_slots()
        max_capacity = ship_storage.max_slots

    if cost is not None and not expedition_manager.cartography_manager.can_travel_to_region(region_id):
        validation_errors.append("region_not_reachable")

    if gold_available < gold_required:
        validation_errors.append("not_enough_gold")

    for item_id, required_amount in required_items.items():
        assigned_amount = assigned_items.get(item_id, 0)

        if assigned_amount < required_amount:
            validation_errors.append("not_enough_required_items")
            break

    if capacity_used > max_capacity:
        validation_errors.append("cargo_capacity_exceeded")

    return ExpeditionSetup(
        region_id=region_id,
        cost=cost,
        travel_requirements=travel_requirements,
        gold_required=gold_required,
        gold_available=gold_available,
        required_items=required_items,
        assigned_items=assigned_items,
        selected_cargo=selected_cargo,
        capacity_used=capacity_used,
        can_launch=len(validation_errors) == 0,
        validation_errors=validation_errors,
    )


def calculate_capacity_used(selected_cargo):
    return len(selected_cargo)
