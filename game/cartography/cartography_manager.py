from game.cartography.cartography_states import HIDDEN, SEEN, EXPLORED, SETTLED
from game.cartography.data.region_database import REGION_DATABASE
from game.cartography.data.port_database import PORT_DATABASE
from game.cartography.ship_storage import ShipStorage


STARTING_REGION_ID = "home_port"


class CartographyManager:
    def __init__(self):
        self.regions = {}
        self.active_anchor_region_id = STARTING_REGION_ID
        self.unlocked_ports = [STARTING_REGION_ID]
        self.ship_storage = ShipStorage()
        self.active_expedition = None
        self.pending_expedition_result = None
        self.pending_expedition_results = []

        self._create_default_state()

    def _create_default_state(self):
        for region_id in REGION_DATABASE:
            self.regions[region_id] = {
                "id": region_id,
                "state": HIDDEN,
                "cartography_percent": 0,
                "visits": 0,
            }

        self.regions[STARTING_REGION_ID]["state"] = SETTLED
        self.regions[STARTING_REGION_ID]["cartography_percent"] = 100

        self.reveal_connected_regions(STARTING_REGION_ID)

    def get_save_data(self):
        return {
            "regions": self.regions,
            "active_anchor_region_id": self.active_anchor_region_id,
            "unlocked_ports": self.unlocked_ports,
            "ship_storage": self.ship_storage.get_save_data(),
            "active_expedition": self.active_expedition,
            "pending_expedition_result": self.pending_expedition_result,
            "pending_expedition_results": self.pending_expedition_results,
        }

    def load_from_data(self, data):
        if not data:
            return

        saved_regions = data.get("regions", {})
        for region_id, region_progress in saved_regions.items():
            if region_id not in self.regions:
                continue

            self.regions[region_id].update(region_progress)

        self.active_anchor_region_id = data.get("active_anchor_region_id", self.active_anchor_region_id)
        self.unlocked_ports = data.get("unlocked_ports", self.unlocked_ports)
        self.ship_storage.load_from_data(data.get("ship_storage"))
        self.active_expedition = data.get("active_expedition")
        self.pending_expedition_results = self.normalize_pending_expedition_results(data)
        self.sync_pending_expedition_result()

    def normalize_pending_expedition_results(self, data):
        pending_results = data.get("pending_expedition_results")

        if isinstance(pending_results, list):
            return [
                pending_result
                for pending_result in pending_results
                if isinstance(pending_result, dict)
            ]

        pending_result = data.get("pending_expedition_result")

        if isinstance(pending_result, dict):
            return [pending_result]

        return []

    def sync_pending_expedition_result(self):
        self.pending_expedition_result = None

        if self.pending_expedition_results:
            self.pending_expedition_result = self.pending_expedition_results[0]

    def add_pending_expedition_result(self, pending_result):
        self.pending_expedition_results.append(pending_result)
        self.sync_pending_expedition_result()

    def has_pending_expedition_results(self):
        return bool(self.pending_expedition_results)

    def get_pending_expedition_results(self):
        return list(self.pending_expedition_results)

    def get_region_state(self, region_id):
        if region_id not in self.regions:
            return None

        return self.regions[region_id]["state"]

    def get_visible_regions(self):
        visible_regions = []

        for region_id, progress_data in self.regions.items():
            if progress_data["state"] != HIDDEN:
                region_data = self.get_region_view_data(region_id)
                visible_regions.append(region_data)

        return visible_regions

    def get_region_view_data(self, region_id):
        if region_id not in REGION_DATABASE or region_id not in self.regions:
            return None

        progress_data = self.regions[region_id]
        region_data = REGION_DATABASE[region_id].copy()
        region_data["state"] = progress_data["state"]
        region_data["cartography_percent"] = progress_data["cartography_percent"]
        region_data["visits"] = progress_data["visits"]
        region_data["hidden"] = progress_data["state"] == HIDDEN
        region_data["visible"] = progress_data["state"] != HIDDEN
        region_data["can_travel"] = self.can_travel_to_region(region_id)
        region_data["is_unlocked_port"] = region_id in self.unlocked_ports
        return region_data

    def get_map_view_data(self, world_map):
        map_rows = []

        for row in world_map:
            map_rows.append([
                self.get_region_view_data(region_id) if region_id is not None else None
                for region_id in row
            ])

        return map_rows

    def get_global_cartography_percent(self):
        if not self.regions:
            return 0

        total_percent = sum(
            region_progress["cartography_percent"]
            for region_progress in self.regions.values()
        )
        return int(total_percent / len(self.regions))

    def can_travel_to_region(self, region_id):
        if region_id not in self.regions:
            return False

        if self.active_anchor_region_id not in REGION_DATABASE:
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
