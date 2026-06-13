from pathlib import Path
from PIL import Image


TRANSPARENT_CHAR = "."
MAX_COLORS = 48


def color_to_char(index):
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

    if index >= len(chars):
        raise ValueError("Demasiados colores únicos incluso tras cuantizar.")

    return chars[index]


def png_to_bitmap(input_path, output_path, variable_name, bitmap_id, pixel_size=1, max_colors=MAX_COLORS):
    image = Image.open(input_path).convert("RGBA")

    alpha = image.getchannel("A")
    rgb_image = image.convert("RGB")
    quantized = rgb_image.quantize(colors=max_colors, method=Image.Quantize.MEDIANCUT).convert("RGB")
    quantized.putalpha(alpha)

    width, height = quantized.size

    palette = {
        TRANSPARENT_CHAR: None,
    }

    color_to_symbol = {}
    next_color_index = 0
    bitmap_rows = []

    for y in range(height):
        row = ""

        for x in range(width):
            r, g, b, a = quantized.getpixel((x, y))
            if r > 245 and g > 245 and b > 245:
                row += TRANSPARENT_CHAR
                continue

            if a == 0:
                row += TRANSPARENT_CHAR
                continue

            color = (r, g, b)

            if color not in color_to_symbol:
                symbol = color_to_char(next_color_index)
                next_color_index += 1

                color_to_symbol[color] = symbol
                palette[symbol] = color

            row += color_to_symbol[color]

        bitmap_rows.append(row)

    output = build_python_file(
        variable_name,
        bitmap_id,
        width,
        height,
        pixel_size,
        palette,
        bitmap_rows,
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output, encoding="utf-8")


def build_python_file(variable_name, bitmap_id, width, height, pixel_size, palette, bitmap_rows):
    lines = []

    lines.append(f"{variable_name} = {{")
    lines.append(f'    "id": "{bitmap_id}",')
    lines.append(f'    "name": "{bitmap_id}",')
    lines.append(f'    "width": {width},')
    lines.append(f'    "height": {height},')
    lines.append(f'    "pixel_size": {pixel_size},')
    lines.append(f'    "collision_width": 2,')
    lines.append(f'    "collision_height": 2,')
    lines.append(f'    "collision_offset_x": 0,')
    lines.append(f'    "collision_offset_y": 1,')
    lines.append('    "palette": {')

    for symbol, color in palette.items():
        if color is None:
            lines.append(f'        "{symbol}": None,')
        else:
            lines.append(f'        "{symbol}": {color},')

    lines.append("    },")
    lines.append('    "bitmap": [')

    for row in bitmap_rows:
        lines.append(f'        "{row}",')

    lines.append("    ],")
    lines.append("}")
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    png_to_bitmap(
        input_path="assets/source_png/tree_oak.png",
        output_path="assets/bitmaps/tree_oak_bitmap.py",
        variable_name="TREE_OAK_BITMAP",
        bitmap_id="tree_oak",
        pixel_size=0.25,
        max_colors=48,
    )