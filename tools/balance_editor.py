import tkinter as tk
from tkinter import ttk, messagebox

from core.data_loader import load_json, save_json


class BalanceEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Balance Editor - Maritime RPG")
        self.root.geometry("900x560")

        self.actions = load_json("actions.json")
        self.routes = load_json("routes.json")
        self.resources = load_json("resources.json")
        self.upgrades = load_json("upgrades.json")
        self.config = load_json("game_config.json")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.build_actions_tab()
        self.build_routes_tab()
        self.build_config_tab()

        save_button = tk.Button(root, text="Guardar JSON", command=self.save_all)
        save_button.pack(side=tk.BOTTOM, pady=8)

    def build_actions_tab(self):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text="Acciones")

        self.actions_tree = ttk.Treeview(frame, columns=("name", "energy", "reward"), show="headings")
        self.actions_tree.heading("name", text="Nombre")
        self.actions_tree.heading("energy", text="Energia")
        self.actions_tree.heading("reward", text="Recompensa")
        self.actions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        form = tk.Frame(frame, padx=10)
        form.pack(side=tk.RIGHT, fill=tk.Y)

        self.action_key = tk.StringVar()
        self.action_name = tk.StringVar()
        self.action_energy = tk.IntVar()
        self.action_reward = tk.StringVar()

        self.add_field(form, "Key", self.action_key)
        self.add_field(form, "Nombre", self.action_name)
        self.add_field(form, "Energia", self.action_energy)
        self.add_field(form, "Reward JSON", self.action_reward)

        tk.Button(form, text="Cargar seleccion", command=self.load_selected_action).pack(fill=tk.X, pady=4)
        tk.Button(form, text="Aplicar", command=self.apply_action).pack(fill=tk.X, pady=4)
        tk.Button(form, text="Nueva accion", command=self.new_action).pack(fill=tk.X, pady=4)

        self.refresh_actions_tree()

    def build_routes_tab(self):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text="Rutas")

        self.routes_tree = ttk.Treeview(frame, columns=("name", "duration", "success", "cost"), show="headings")
        self.routes_tree.heading("name", text="Nombre")
        self.routes_tree.heading("duration", text="Dias")
        self.routes_tree.heading("success", text="Exito")
        self.routes_tree.heading("cost", text="Coste")
        self.routes_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        form = tk.Frame(frame, padx=10)
        form.pack(side=tk.RIGHT, fill=tk.Y)

        self.route_key = tk.StringVar()
        self.route_name = tk.StringVar()
        self.route_duration = tk.IntVar()
        self.route_success = tk.IntVar()
        self.route_cost = tk.StringVar()
        self.route_safe_reward = tk.StringVar()
        self.route_risk_reward = tk.StringVar()

        self.add_field(form, "Key", self.route_key)
        self.add_field(form, "Nombre", self.route_name)
        self.add_field(form, "Dias", self.route_duration)
        self.add_field(form, "Exito base", self.route_success)
        self.add_field(form, "Coste JSON", self.route_cost)
        self.add_field(form, "Seguro JSON", self.route_safe_reward)
        self.add_field(form, "Riesgo JSON", self.route_risk_reward)

        tk.Button(form, text="Cargar seleccion", command=self.load_selected_route).pack(fill=tk.X, pady=4)
        tk.Button(form, text="Aplicar", command=self.apply_route).pack(fill=tk.X, pady=4)
        tk.Button(form, text="Nueva ruta", command=self.new_route).pack(fill=tk.X, pady=4)

        self.refresh_routes_tree()

    def build_config_tab(self):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text="Config")

        self.max_energy = tk.IntVar(value=self.config["max_energy"])
        self.max_health = tk.IntVar(value=self.config["max_health"])
        self.season_days = tk.IntVar(value=self.config["season_days"])

        self.add_field(frame, "Energia maxima", self.max_energy)
        self.add_field(frame, "Vida maxima", self.max_health)
        self.add_field(frame, "Dias por estacion", self.season_days)

        tk.Button(frame, text="Aplicar config", command=self.apply_config).pack(anchor="w", padx=10, pady=10)

    def add_field(self, parent, label, variable):
        tk.Label(parent, text=label).pack(anchor="w", pady=(8, 0))
        tk.Entry(parent, textvariable=variable, width=34).pack(anchor="w")

    def refresh_actions_tree(self):
        self.actions_tree.delete(*self.actions_tree.get_children())
        for key, action in self.actions.items():
            self.actions_tree.insert("", "end", iid=key, values=(action["name"], action["energy_cost"], action["reward"]))

    def refresh_routes_tree(self):
        self.routes_tree.delete(*self.routes_tree.get_children())
        for key, route in self.routes.items():
            self.routes_tree.insert("", "end", iid=key, values=(route["name"], route["duration"], route["base_success"], route["cost"]))

    def load_selected_action(self):
        selected = self.actions_tree.selection()
        if not selected:
            return
        key = selected[0]
        action = self.actions[key]
        self.action_key.set(key)
        self.action_name.set(action["name"])
        self.action_energy.set(action["energy_cost"])
        self.action_reward.set(str(action["reward"]))

    def apply_action(self):
        key = self.action_key.get().strip()
        if not key:
            return
        try:
            reward = eval(self.action_reward.get(), {}, {})
        except Exception as error:
            messagebox.showerror("Error", f"Reward invalido: {error}")
            return

        old = self.actions.get(key, {})
        self.actions[key] = {
            "name": self.action_name.get(),
            "zone": old.get("zone", "farm"),
            "energy_cost": int(self.action_energy.get()),
            "reward": reward,
            "message": old.get("message", "Accion completada."),
        }
        self.refresh_actions_tree()

    def new_action(self):
        self.action_key.set("new_action")
        self.action_name.set("Nueva accion")
        self.action_energy.set(3)
        self.action_reward.set("{'food': [1, 3]}")

    def load_selected_route(self):
        selected = self.routes_tree.selection()
        if not selected:
            return
        key = selected[0]
        route = self.routes[key]
        self.route_key.set(key)
        self.route_name.set(route["name"])
        self.route_duration.set(route["duration"])
        self.route_success.set(route["base_success"])
        self.route_cost.set(str(route["cost"]))
        self.route_safe_reward.set(str(route["safe_reward"]))
        self.route_risk_reward.set(str(route["risk_reward"]))

    def apply_route(self):
        key = self.route_key.get().strip()
        if not key:
            return
        try:
            cost = eval(self.route_cost.get(), {}, {})
            safe_reward = eval(self.route_safe_reward.get(), {}, {})
            risk_reward = eval(self.route_risk_reward.get(), {}, {})
        except Exception as error:
            messagebox.showerror("Error", f"JSON invalido: {error}")
            return

        old = self.routes.get(key, {})
        self.routes[key] = {
            "name": self.route_name.get(),
            "direction": old.get("direction", "east"),
            "duration": int(self.route_duration.get()),
            "base_success": int(self.route_success.get()),
            "season_block": old.get("season_block", []),
            "requires": old.get("requires", {}),
            "cost": cost,
            "safe_reward": safe_reward,
            "risk_reward": risk_reward,
            "description": old.get("description", "Nueva ruta."),
        }
        self.refresh_routes_tree()

    def new_route(self):
        self.route_key.set("new_route")
        self.route_name.set("Nueva ruta")
        self.route_duration.set(3)
        self.route_success.set(70)
        self.route_cost.set("{'food': 3, 'wood': 3}")
        self.route_safe_reward.set("{'gold': 80}")
        self.route_risk_reward.set("{'gold': 150}")

    def apply_config(self):
        self.config["max_energy"] = int(self.max_energy.get())
        self.config["max_health"] = int(self.max_health.get())
        self.config["season_days"] = int(self.season_days.get())
        messagebox.showinfo("Config", "Config aplicada. Pulsa Guardar JSON.")

    def save_all(self):
        save_json("actions.json", self.actions)
        save_json("routes.json", self.routes)
        save_json("resources.json", self.resources)
        save_json("upgrades.json", self.upgrades)
        save_json("game_config.json", self.config)
        messagebox.showinfo("Guardado", "Datos guardados en JSON.")


def main():
    root = tk.Tk()
    BalanceEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
