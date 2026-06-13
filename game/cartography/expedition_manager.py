from game.cartography.data.region_database import REGION_DATABASE
from game.cartography.reward_generator import generate_region_rewards


DEFAULT_EXPEDITION_DAYS = 1
DEFAULT_EXPEDITION_RISK = 1
DEFAULT_TRAVEL_REQUIREMENTS = {
    "gold": 0,
    "items": {},
    "crew": {},
    "ship_upgrades": [],
    "monsters": {},
}


class ExpeditionManager:
    def __init__(self, cartography_manager):
        self.cartography_manager = cartography_manager
        if self.active_expedition is not None:
            self.active_expedition = self.normalize_active_expedition(
                self.active_expedition
            )

    @property
    def active_expedition(self):
        return self.cartography_manager.active_expedition

    @active_expedition.setter
    def active_expedition(self, value):
        self.cartography_manager.active_expedition = value

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
            "risk": danger,
            "travel_requirements": self.get_travel_requirements(region_id),
        }

    def get_travel_requirements(self, region_id):
        if region_id not in REGION_DATABASE:
            return None

        region_requirements = REGION_DATABASE[region_id].get("travel_requirements", {})
        requirements = {
            "gold": region_requirements.get("gold", DEFAULT_TRAVEL_REQUIREMENTS["gold"]),
            "items": region_requirements.get("items", DEFAULT_TRAVEL_REQUIREMENTS["items"]).copy(),
            "crew": region_requirements.get("crew", DEFAULT_TRAVEL_REQUIREMENTS["crew"]).copy(),
            "ship_upgrades": list(region_requirements.get("ship_upgrades", DEFAULT_TRAVEL_REQUIREMENTS["ship_upgrades"])),
            "monsters": region_requirements.get("monsters", DEFAULT_TRAVEL_REQUIREMENTS["monsters"]).copy(),
        }
        return requirements

    def start_expedition(self, region_id, assigned_resources=None, assigned_crew=None):
        if assigned_resources is None:
            assigned_resources = {}

        if assigned_crew is None:
            assigned_crew = []

        if self.active_expedition is not None:
            return {
                "success": False,
                "reason": "active_expedition_exists",
            }

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

        requirements = cost["travel_requirements"]
        assigned_gold = assigned_resources.get("gold", 0)

        if assigned_gold < requirements["gold"]:
            return {
                "success": False,
                "reason": "not_enough_gold",
                "required_gold": requirements["gold"],
            }

        assigned_items = assigned_resources.get("items", {})
        missing_items = {}

        for item_id, required_amount in requirements["items"].items():
            assigned_amount = assigned_items.get(item_id, 0)

            if assigned_amount < required_amount:
                missing_items[item_id] = required_amount

        if missing_items:
            return {
                "success": False,
                "reason": "not_enough_required_items",
                "missing_items": missing_items,
            }

        self.active_expedition = {
            "region_id": region_id,
            "total_days": cost["days"],
            "remaining_days": cost["days"],
            "assigned_resources": assigned_resources,
            "assigned_crew": assigned_crew,
            "cost": cost,
        }

        return {
            "success": True,
            "expedition": self.active_expedition,
        }

    def advance_active_expedition_day(self):
        if self.active_expedition is None:
            return {
                "success": False,
                "reason": "no_active_expedition",
            }

        expedition = self.normalize_active_expedition(self.active_expedition)

        if expedition["remaining_days"] <= 0:
            self.active_expedition = expedition
            return {
                "success": False,
                "reason": "active_expedition_completed",
                "region_id": expedition["region_id"],
                "remaining_days": expedition["remaining_days"],
                "total_days": expedition["total_days"],
            }

        expedition["remaining_days"] = max(0, expedition["remaining_days"] - 1)
        self.active_expedition = expedition

        return {
            "success": True,
            "region_id": expedition["region_id"],
            "remaining_days": expedition["remaining_days"],
            "total_days": expedition["total_days"],
            "completed": expedition["remaining_days"] == 0,
        }

    def normalize_active_expedition(self, expedition):
        cost = expedition.get("cost", {})
        total_days = expedition.get("total_days", cost.get("days", 0))
        remaining_days = expedition.get("remaining_days", total_days)

        return {
            "region_id": expedition["region_id"],
            "total_days": total_days,
            "remaining_days": remaining_days,
            "assigned_resources": expedition.get("assigned_resources", {}),
            "assigned_crew": expedition.get("assigned_crew", []),
            "cost": cost,
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
