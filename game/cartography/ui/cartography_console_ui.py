from game.cartography.data.region_database import REGION_DATABASE
from game.cartography.data.port_database import PORT_DATABASE


class CartographyConsoleUI:
    def __init__(self, cartography_manager, expedition_manager):
        self.cartography_manager = cartography_manager
        self.expedition_manager = expedition_manager

    def print_visible_map(self):
        visible_regions = self.cartography_manager.get_visible_regions()

        print("")
        print("=== MAPA CARTOGRÁFICO ===")
        print("Anclaje actual:", self.cartography_manager.active_anchor_region_id)
        print("")

        for region in visible_regions:
            region_id = region["id"]
            name = region["name"]
            state = region["state"]
            percent = region["cartography_percent"]

            reachable = self.cartography_manager.can_travel_to_region(region_id)

            marker = "-"
            if reachable:
                marker = ">"

            print(f"{marker} {region_id} | {name} | {state} | {percent}%")

    def print_region_detail(self, region_id):
        if region_id not in REGION_DATABASE:
            print("Región no encontrada.")
            return

        region = REGION_DATABASE[region_id]
        progress = self.cartography_manager.regions.get(region_id, {})

        print("")
        print("=== DETALLE DE REGIÓN ===")
        print("ID:", region_id)
        print("Nombre:", region["name"])
        print("Descripción:", region["description"])
        print("Estado:", progress.get("state"))
        print("Cartografía:", str(progress.get("cartography_percent")) + "%")
        print("Conexiones:", ", ".join(region.get("connections", [])))
        print("Días base:", region.get("base_days"))
        print("Peligro:", region.get("danger"))
        print("Tiene puerto:", region.get("has_port"))

    def print_ports(self):
        print("")
        print("=== PUERTOS ===")

        for port_id, port_data in PORT_DATABASE.items():
            region_id = port_data["region_id"]
            state = self.cartography_manager.get_region_state(region_id)
            unlocked = region_id in self.cartography_manager.unlocked_ports

            print("")
            print(port_id, "|", port_data["name"])
            print("Región:", region_id)
            print("Estado región:", state)
            print("Desbloqueado:", unlocked)
            print("Requisitos:", port_data.get("requirements", {}))
