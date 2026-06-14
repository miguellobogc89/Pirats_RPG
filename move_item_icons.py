from pathlib import Path
import shutil

base = Path("assets/items")

category_by_file = {
    "weapons": ["sword", "spear", "bow", "staff"],
    "tools": ["axe", "pickaxe", "shovel", "hammer", "hoe", "watering_can", "fishing_rod"],
    "armor": ["boots", "chestplate", "gloves", "helmet", "pants", "cap", "tunic", "hat"],
    "resources": ["ore", "ingot", "wood", "stone", "coal", "carbon", "log", "plank", "stick", "gold", "iron"],
    "gems": ["amethyst", "citrine", "emerald", "ruby", "sapphire", "topaz"],
    "food": ["apple", "carrot", "corn", "egg", "fried_egg", "meat", "mushroom", "food"],
    "potions": ["potion"],
    "books_scrolls": ["book", "scroll"],
    "keys": ["key"],
    "ammo": ["arrow"],
    "rings": ["ring"],
    "shields": ["shield"],
    "seeds_crops": ["seed"],
    "building": ["campfire", "wood_floor"],
}

for file in base.glob("*.png"):
    name = file.stem
    target_category = "misc"

    for category, keywords in category_by_file.items():
        for keyword in keywords:
            if keyword in name:
                target_category = category
                break
        if target_category != "misc":
            break

    target_dir = base / target_category
    target_dir.mkdir(exist_ok=True)

    target_path = target_dir / file.name
    shutil.move(str(file), str(target_path))
    print(f"{file.name} -> {target_category}/{file.name}")