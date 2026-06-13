from game.cartography.cartography_states import HIDDEN, SEEN, EXPLORED, SETTLED
from game.cartography.region_database import REGION_DATABASE
from game.cartography.port_database import PORT_DATABASE
from game.cartography.cartography_save import load_cartography_save, save_cartography_data


class CartographyManager:
    def __init__(self):
        self.regions = {}
        self.active_anchor_region_id = "home_port"
        self.unlocked_ports = ["home_port"]

        self._create_default_state()

    def _create_default_state(self):
        for region_id in REGION_DATABASE:
            self.regions[region_id] = {
                "id": region_id,
                "state": HIDDEN,
                "cartography_percent": 0,
                "visits": 0,
            }

        self.regions["home_port"]["state"] = SETTLED
        self.regions["home_port"]["cartography_percent"] = 100

        self.reveal_connected_regions("home_port")

    def get_save_data(self):
        return {
            "regions": self.regions,
            "active_anchor_region_id": self.active_anchor_region_id,
            "unlocked_ports": self.unlocked_ports,
        }

    def load_from_data(self, data):
        if not data:
            return

        self.regions = data.get("regions", self.regions)
        self.active_anchor_region_id = data.get("active_anchor_region_id", self.active_anchor_region_id)
        self.unlocked_ports = data.get("unlocked_ports", self.unlocked_ports)

    def save(self):
        save_cartography_data(self.get_save_data())

    def load(self):
        data = load_cartography_save()
        self.load_from_data(data)

    def get_region_state(self, region_id):
        if region_id not in self.regions:
            return None

        return self.regions[region_id]["state"]

    def get_visible_regions(self):
        visible_regions = []

        for region_id, progress_data in self.regions.items():
            if progress_data["state"] != HIDDEN:
                region_data = REGION_DATABASE[region_id].copy()
                region_data["state"] = progress_data["state"]
                region_data["cartography_percent"] = progress_data["cartography_percent"]
                region_data["visits"] = progress_data["visits"]
                visible_regions.append(region_data)

        return visible_regions

    def can_travel_to_region(self, region_id):
        if region_id not in self.regions:
            return False

        region_state = self.regions[region_id]["state"]

        if region_state == HIDDEN:
            return False

        anchor_data = REGION_DATABASE[self.active_anchor_region_id]
        connections = anchor_data.get("connections", [])

        if region_id in connections:
            return True

        return False

    def reveal_connected_regions(self, region_id):
        if region_id not in REGION_DATABASE:
            return

        connections = REGION_DATABASE[region_id].get("connections", [])

        for connected_region_id in connections:
            if connected_region_id not in self.regions:
                continue

            if self.regions[connected_region_id]["state"] == HIDDEN:
                self.regions[connected_region_id]["state"] = SEEN
                self.regions[connected_region_id]["cartography_percent"] = 25

    def explore_region(self, region_id):
        if region_id not in self.regions:
            return {
                "success": False,
                "reason": "region_not_found",
            }

        if self.regions[region_id]["state"] == HIDDEN:
            return {
                "success": False,
                "reason": "region_hidden",
            }

        self.regions[region_id]["visits"] += 1

        current_percent = self.regions[region_id]["cartography_percent"]
        new_percent = current_percent + 25

        if new_percent > 100:
            new_percent = 100

        self.regions[region_id]["cartography_percent"] = new_percent

        if new_percent >= 50 and self.regions[region_id]["state"] == SEEN:
            self.regions[region_id]["state"] = EXPLORED

        self.reveal_connected_regions(region_id)

        return {
            "success": True,
            "region_id": region_id,
            "cartography_percent": self.regions[region_id]["cartography_percent"],
            "state": self.regions[region_id]["state"],
        }

    def can_settle_port(self, port_id, available_resources):
        if port_id not in PORT_DATABASE:
            return False

        port_data = PORT_DATABASE[port_id]
        requirements = port_data.get("requirements", {})

        for item_id, required_amount in requirements.items():
            available_amount = available_resources.get(item_id, 0)

            if available_amount < required_amount:
                return False

        return True

    def settle_port(self, port_id, available_resources):
        if port_id not in PORT_DATABASE:
            return {
                "success": False,
                "reason": "port_not_found",
            }

        if not self.can_settle_port(port_id, available_resources):
            return {
                "success": False,
                "reason": "missing_resources",
            }

        port_data = PORT_DATABASE[port_id]
        region_id = port_data["region_id"]

        if region_id not in self.regions:
            return {
                "success": False,
                "reason": "region_not_found",
            }

        self.regions[region_id]["state"] = SETTLED
        self.regions[region_id]["cartography_percent"] = 100

        if region_id not in self.unlocked_ports:
            self.unlocked_ports.append(region_id)

        self.reveal_connected_regions(region_id)

        return {
            "success": True,
            "region_id": region_id,
            "port_id": port_id,
        }

    def set_active_anchor(self, region_id):
        if region_id not in self.unlocked_ports:
            return False

        self.active_anchor_region_id = region_id
        return True
