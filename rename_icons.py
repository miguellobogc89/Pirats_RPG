from pathlib import Path
import re

folder = Path("assets/items")

for file in folder.glob("*.png"):
    new_name = file.stem.lower()
    new_name = new_name.replace(" ", "_")
    new_name = new_name.replace("-", "_")
    new_name = re.sub(r"_+", "_", new_name)

    new_file = file.with_name(new_name + ".png")

    if file != new_file:
        file.rename(new_file)
        print(f"{file.name} -> {new_file.name}")