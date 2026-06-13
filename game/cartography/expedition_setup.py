from dataclasses import dataclass, field

from game.cartography.expedition_manager import SUPPLY_RESOURCE_ID


@dataclass
class ExpeditionSetup:
    region_id: str
    cost: dict
    provisions_required: int
    provisions_assigned: int = 0
    selected_cargo: list = field(default_factory=list)
    capacity_used: int = 0
    can_launch: bool = False
    validation_errors: list = field(default_factory=list)

    def get_assigned_resources(self):
        return {
            SUPPLY_RESOURCE_ID: self.provisions_assigned,
        }


def create_expedition_setup(
    region_id,
    expedition_manager,
    ship_storage,
    provisions_assigned=None,
    selected_cargo=None,
):
    cost = expedition_manager.calculate_expedition_cost(region_id)
    validation_errors = []

    if cost is None:
        cost = {}
        provisions_required = 0
        validation_errors.append("region_not_found")
    else:
        provisions_required = cost["supplies"]

    # TODO: conectar este valor a bodega/inventario cuando exista el flujo
    # de asignacion real. Mientras tanto conserva el comportamiento actual:
    # preparar una expedicion asigna automaticamente el minimo requerido.
    if provisions_assigned is None:
        provisions_assigned = provisions_required

    if selected_cargo is None:
        selected_cargo = []

    capacity_used = calculate_capacity_used(selected_cargo)

    if not expedition_manager.cartography_manager.can_travel_to_region(region_id):
        validation_errors.append("region_not_reachable")

    if provisions_assigned < provisions_required:
        validation_errors.append("not_enough_supplies")

    if capacity_used > ship_storage.max_slots:
        validation_errors.append("cargo_capacity_exceeded")

    return ExpeditionSetup(
        region_id=region_id,
        cost=cost,
        provisions_required=provisions_required,
        provisions_assigned=provisions_assigned,
        selected_cargo=selected_cargo,
        capacity_used=capacity_used,
        can_launch=len(validation_errors) == 0,
        validation_errors=validation_errors,
    )


def calculate_capacity_used(selected_cargo):
    return len(selected_cargo)
