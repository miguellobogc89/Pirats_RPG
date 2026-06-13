from game.cartography.data.region_database import REGION_DATABASE
from game.cartography.reward_generator import generate_region_rewards


SUPPLY_RESOURCE_ID = "supplies"
SUPPLIES_PER_TRAVEL_DAY = 2
DEFAULT_EXPEDITION_DAYS = 1
DEFAULT_EXPEDITION_RISK = 1


class ExpeditionManager:
    def __init__(self, cartography_manager):
        self.cartography_manager = cartography_manager
        self.active_expedition = None

    def calculate_expedition_cost(self, region_id):
        if region_id not in REGION_DATABASE:
            return None

        region_data = REGION_DATABASE[region_id]
        base_days = region_data.get(
            "base_days",
            region_data.get("travel_days", DEFAULT_EXPEDITION_DAYS),
        )
        danger = region_data.get("danger", DEFAULT_EXPEDITION_RISK)

        return {
            "days": base_days,
            # TODO: sustituir esta regla temporal cuando bodega/inventario
            # definan provisiones reales por expedicion.
            "supplies": base_days * SUPPLIES_PER_TRAVEL_DAY,
            "risk": danger,
        }

    def start_expedition(self, region_id, assigned_resources=None, assigned_crew=None):
        if assigned_resources is None:
            assigned_resources = {}

        if assigned_crew is None:
            assigned_crew = []

        if not self.cartography_manager.can_travel_to_region(region_id):
            return {
                "success": False,
                "reason": "region_not_reachable",
            }

        cost = self.calculate_expedition_cost(region_id)

        if cost is None:
            return {
                "success": False,
                "reason": "region_not_found",
            }

        supplies = assigned_resources.get(SUPPLY_RESOURCE_ID, 0)

        if supplies < cost["supplies"]:
            return {
                "success": False,
                "reason": "not_enough_supplies",
                "required_supplies": cost["supplies"],
            }

        self.active_expedition = {
            "region_id": region_id,
            "assigned_resources": assigned_resources,
            "assigned_crew": assigned_crew,
            "cost": cost,
        }

        return {
            "success": True,
            "expedition": self.active_expedition,
        }

    def resolve_active_expedition(self):
        if self.active_expedition is None:
            return {
                "success": False,
                "reason": "no_active_expedition",
            }

        region_id = self.active_expedition["region_id"]
        region_data = REGION_DATABASE[region_id]

        explore_result = self.cartography_manager.explore_region(region_id)
        rewards = generate_region_rewards(region_data)

        result = {
            "success": True,
            "region_id": region_id,
            "explore_result": explore_result,
            "rewards": rewards,
            "cost": self.active_expedition["cost"],
        }

        self.active_expedition = None

        return result
