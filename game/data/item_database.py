DEFAULT_STACKABLE_MAX_STACK = 99
DEFAULT_UNSTACKABLE_MAX_STACK = 1


ITEM_DATABASE = {
    'amethyst': {
    'name': 'Amatista', 'type': 'gem', 'icon': 'A', 'sprite': 'assets/items/gems/amethyst.png', 'stackable': True},
    'amethyst_ring': {
    'name': 'Amatista anillo', 'type': 'ring', 'icon': 'A', 'sprite': 'assets/items/rings/amethyst_ring.png', 'stackable': False},
    'ancient_axe': {
    'name': 'Antiguo hacha', 'type': 'tool', 'icon': 'A', 'sprite': 'assets/items/tools/ancient_axe.png', 'stackable': False, 'tool_type': 'axe'},
    'ancient_boots': {
    'name': 'Antiguo botas', 'type': 'armor', 'icon': 'A', 'sprite': 'assets/items/armor/ancient_boots.png', 'stackable': False},
    'ancient_chestplate': {
    'name': 'Antiguo coraza', 'type': 'armor', 'icon': 'A', 'sprite': 'assets/items/armor/ancient_chestplate.png', 'stackable': False},
    'ancient_gloves': {
    'name': 'Antiguo guantes', 'type': 'armor', 'icon': 'A', 'sprite': 'assets/items/armor/ancient_gloves.png', 'stackable': False},
    'ancient_hammer': {
    'name': 'Antiguo martillo', 'type': 'tool', 'icon': 'A', 'sprite': 'assets/items/tools/ancient_hammer.png', 'stackable': False, 'tool_type': 'hammer'},
    'ancient_helmet': {
    'name': 'Antiguo yelmo', 'type': 'armor', 'icon': 'A', 'sprite': 'assets/items/armor/ancient_helmet.png', 'stackable': False},
    'ancient_ingot': {
    'name': 'Antiguo lingote', 'type': 'resource', 'icon': 'A', 'sprite': 'assets/items/resources/ancient_ingot.png', 'stackable': True},
    'ancient_ore': {
    'name': 'Antiguo mineral', 'type': 'resource', 'icon': 'A', 'sprite': 'assets/items/resources/ancient_ore.png', 'stackable': True},
    'ancient_pants': {
    'name': 'Antiguo pantalones', 'type': 'armor', 'icon': 'A', 'sprite': 'assets/items/armor/ancient_pants.png', 'stackable': False},
    'ancient_pickaxe': {
    'name': 'Antiguo pico', 'type': 'tool', 'icon': 'A', 'sprite': 'assets/items/tools/ancient_pickaxe.png', 'stackable': False, 'tool_type': 'axe'},
    'ancient_shovel': {
    'name': 'Antiguo pala', 'type': 'tool', 'icon': 'A', 'sprite': 'assets/items/tools/ancient_shovel.png', 'stackable': False, 'tool_type': 'shovel'},
    'ancient_spear': {
    'name': 'Antiguo lanza', 'type': 'weapon', 'icon': 'A', 'sprite': 'assets/items/weapons/ancient_spear.png', 'stackable': False},
    'ancient_sword': {
    'name': 'Antiguo espada', 'type': 'weapon', 'icon': 'A', 'sprite': 'assets/items/weapons/ancient_sword.png', 'stackable': False},
    'apple': {
    'name': 'Manzana', 'type': 'food', 'icon': 'A', 'sprite': 'assets/items/food/apple.png', 'stackable': True},
    'arrow': {
    'name': 'Flecha', 'type': 'ammo', 'icon': 'A', 'sprite': 'assets/items/ammo/arrow.png', 'stackable': True},
    'axe': {
    'name': 'Hacha', 'type': 'tool', 'icon': 'A', 'sprite': 'assets/items/tools/axe.png', 'stackable': False, 'tool_type': 'axe'},
    'black_pearl': {
    'name': 'Perla negra', 'type': 'resource', 'icon': 'B', 'stackable': True},
    'blue_feathered_arrow': {
    'name': 'Azul emplumada flecha', 'type': 'ammo', 'icon': 'B', 'sprite': 'assets/items/ammo/blue_feathered_arrow.png', 'stackable': True},
    'blue_scroll': {
    'name': 'Azul pergamino', 'type': 'book', 'icon': 'B', 'sprite': 'assets/items/books_scrolls/blue_scroll.png', 'stackable': True},
    'bow_and_arrow': {
    'name': 'Arco and flecha', 'type': 'ammo', 'icon': 'B', 'sprite': 'assets/items/ammo/bow_and_arrow.png', 'stackable': True},
    'campfire': {
    'name': 'Hoguera', 'type': 'placeable', 'icon': 'C', 'sprite': 'assets/items/building/campfire.png', 'stackable': True, 'footprint': [2, 2]},
    'carbon': {
    'name': 'Carbón', 'type': 'resource', 'icon': 'C', 'sprite': 'assets/items/resources/carbon.png', 'stackable': True},
    'carrot': {
    'name': 'Zanahoria', 'type': 'food', 'icon': 'C', 'sprite': 'assets/items/food/carrot.png', 'stackable': True},
    'citrine': {
    'name': 'Citrino', 'type': 'gem', 'icon': 'C', 'sprite': 'assets/items/gems/citrine.png', 'stackable': True},
    'coal': {
    'name': 'Carbón', 'type': 'resource', 'icon': 'C', 'sprite': 'assets/items/resources/coal.png', 'stackable': True},
    'compass': {
    'name': 'Brújula', 'type': 'misc', 'icon': 'C', 'sprite': 'assets/items/misc/compass.png', 'stackable': True},
    'copper_axe': {
    'name': 'Cobre hacha', 'type': 'tool', 'icon': 'C', 'sprite': 'assets/items/tools/copper_axe.png', 'stackable': False, 'tool_type': 'axe'},
    'copper_boots': {
    'name': 'Cobre botas', 'type': 'armor', 'icon': 'C', 'sprite': 'assets/items/armor/copper_boots.png', 'stackable': False},
    'copper_chestplate': {
    'name': 'Cobre coraza', 'type': 'armor', 'icon': 'C', 'sprite': 'assets/items/armor/copper_chestplate.png', 'stackable': False},
    'copper_gloves': {
    'name': 'Cobre guantes', 'type': 'armor', 'icon': 'C', 'sprite': 'assets/items/armor/copper_gloves.png', 'stackable': False},
    'copper_hammer': {
    'name': 'Cobre martillo', 'type': 'tool', 'icon': 'C', 'sprite': 'assets/items/tools/copper_hammer.png', 'stackable': False, 'tool_type': 'hammer'},
    'copper_helmet': {
    'name': 'Cobre yelmo', 'type': 'armor', 'icon': 'C', 'sprite': 'assets/items/armor/copper_helmet.png', 'stackable': False},
    'copper_ingot': {
    'name': 'Cobre lingote', 'type': 'resource', 'icon': 'C', 'sprite': 'assets/items/resources/copper_ingot.png', 'stackable': True},
    'copper_key': {
    'name': 'Cobre llave', 'type': 'key', 'icon': 'C', 'sprite': 'assets/items/keys/copper_key.png', 'stackable': True},
    'copper_ore': {
    'name': 'Cobre mineral', 'type': 'resource', 'icon': 'C', 'sprite': 'assets/items/resources/copper_ore.png', 'stackable': True},
    'copper_pants': {
    'name': 'Cobre pantalones', 'type': 'armor', 'icon': 'C', 'sprite': 'assets/items/armor/copper_pants.png', 'stackable': False},
    'copper_pickaxe': {
    'name': 'Cobre pico', 'type': 'tool', 'icon': 'C', 'sprite': 'assets/items/tools/copper_pickaxe.png', 'stackable': False, 'tool_type': 'axe'},
    'copper_shovel': {
    'name': 'Cobre pala', 'type': 'tool', 'icon': 'C', 'sprite': 'assets/items/tools/copper_shovel.png', 'stackable': False, 'tool_type': 'shovel'},
    'copper_spear': {
    'name': 'Cobre lanza', 'type': 'weapon', 'icon': 'C', 'sprite': 'assets/items/weapons/copper_spear.png', 'stackable': False},
    'copper_sword': {
    'name': 'Cobre espada', 'type': 'weapon', 'icon': 'C', 'sprite': 'assets/items/weapons/copper_sword.png', 'stackable': False},
    'coral_fragment': {
    'name': 'Fragmento de coral', 'type': 'resource', 'icon': 'C', 'stackable': True},
    'corn': {
    'name': 'Maíz', 'type': 'crop', 'icon': 'C', 'sprite': 'assets/items/food/corn.png', 'stackable': True},
    'corn_seed': {
    'name': 'Semilla de maíz', 'type': 'seed', 'icon': 'C', 'sprite': 'assets/items/seeds_crops/corn_seed.png', 'stackable': True, 'crop_id': 'corn'},
    'dark_axe': {
    'name': 'Oscuro hacha', 'type': 'tool', 'icon': 'D', 'sprite': 'assets/items/tools/dark_axe.png', 'stackable': False, 'tool_type': 'axe'},
    'dark_book': {
    'name': 'Oscuro libro', 'type': 'book', 'icon': 'D', 'sprite': 'assets/items/books_scrolls/dark_book.png', 'stackable': True},
    'dark_boots': {
    'name': 'Oscuro botas', 'type': 'armor', 'icon': 'D', 'sprite': 'assets/items/armor/dark_boots.png', 'stackable': False},
    'dark_chestplate': {
    'name': 'Oscuro coraza', 'type': 'armor', 'icon': 'D', 'sprite': 'assets/items/armor/dark_chestplate.png', 'stackable': False},
    'dark_gloves': {
    'name': 'Oscuro guantes', 'type': 'armor', 'icon': 'D', 'sprite': 'assets/items/armor/dark_gloves.png', 'stackable': False},
    'dark_hammer': {
    'name': 'Oscuro martillo', 'type': 'tool', 'icon': 'D', 'sprite': 'assets/items/tools/dark_hammer.png', 'stackable': False, 'tool_type': 'hammer'},
    'dark_helmet': {
    'name': 'Oscuro yelmo', 'type': 'armor', 'icon': 'D', 'sprite': 'assets/items/armor/dark_helmet.png', 'stackable': False},
    'dark_ingot': {
    'name': 'Oscuro lingote', 'type': 'resource', 'icon': 'D', 'sprite': 'assets/items/resources/dark_ingot.png', 'stackable': True},
    'dark_ore': {
    'name': 'Oscuro mineral', 'type': 'resource', 'icon': 'D', 'sprite': 'assets/items/resources/dark_ore.png', 'stackable': True},
    'dark_pants': {
    'name': 'Oscuro pantalones', 'type': 'armor', 'icon': 'D', 'sprite': 'assets/items/armor/dark_pants.png', 'stackable': False},
    'dark_pickaxe': {
    'name': 'Oscuro pico', 'type': 'tool', 'icon': 'D', 'sprite': 'assets/items/tools/dark_pickaxe.png', 'stackable': False, 'tool_type': 'axe'},
    'dark_shovel': {
    'name': 'Oscuro pala', 'type': 'tool', 'icon': 'D', 'sprite': 'assets/items/tools/dark_shovel.png', 'stackable': False, 'tool_type': 'shovel'},
    'dark_spear': {
    'name': 'Oscuro lanza', 'type': 'weapon', 'icon': 'D', 'sprite': 'assets/items/weapons/dark_spear.png', 'stackable': False},
    'dark_staff': {
    'name': 'Oscuro bastón', 'type': 'weapon', 'icon': 'D', 'sprite': 'assets/items/weapons/dark_staff.png', 'stackable': False},
    'dark_sword': {
    'name': 'Oscuro espada', 'type': 'weapon', 'icon': 'D', 'sprite': 'assets/items/weapons/dark_sword.png', 'stackable': False},
    'driftwood': {
    'name': 'Madera deriva', 'type': 'resource', 'icon': 'D', 'stackable': True},
    'egg': {
    'name': 'Huevo', 'type': 'food', 'icon': 'E', 'sprite': 'assets/items/food/egg.png', 'stackable': True},
    'emerald': {
    'name': 'Esmeralda', 'type': 'gem', 'icon': 'E', 'sprite': 'assets/items/gems/emerald.png', 'stackable': True},
    'emerald_ring': {
    'name': 'Esmeralda anillo', 'type': 'ring', 'icon': 'E', 'sprite': 'assets/items/rings/emerald_ring.png', 'stackable': False},
    'empty_large_potion': {
    'name': 'Vacía grande poción', 'type': 'potion', 'icon': 'E', 'sprite': 'assets/items/potions/empty_large_potion.png', 'stackable': True},
    'empty_regular_potion': {
    'name': 'Vacía normal poción', 'type': 'potion', 'icon': 'E', 'sprite': 'assets/items/potions/empty_regular_potion.png', 'stackable': True},
    'fishing_rod': {
    'name': 'Caña', 'type': 'tool', 'icon': 'F', 'sprite': 'assets/items/tools/fishing_rod.png', 'stackable': False, 'tool_type': 'fishing_rod'},
    'food': {
    'name': 'Comida', 'type': 'food', 'icon': 'F', 'sprite': 'assets/items/food/food.png', 'stackable': True},
    'fried_egg': {
    'name': 'Huevo frito', 'type': 'food', 'icon': 'F', 'sprite': 'assets/items/food/fried_egg.png', 'stackable': True},
    'gem_book': {
    'name': 'Gema libro', 'type': 'book', 'icon': 'G', 'sprite': 'assets/items/books_scrolls/gem_book.png', 'stackable': True},
    'gold': {
    'name': 'Oro', 'type': 'resource', 'icon': 'G', 'sprite': 'assets/items/resources/gold.png', 'stackable': True},
    'gold_axe': {
    'name': 'Oro hacha', 'type': 'tool', 'icon': 'G', 'sprite': 'assets/items/tools/gold_axe.png', 'stackable': False, 'tool_type': 'axe'},
    'gold_boots': {
    'name': 'Oro botas', 'type': 'armor', 'icon': 'G', 'sprite': 'assets/items/armor/gold_boots.png', 'stackable': False},
    'gold_chestplate': {
    'name': 'Oro coraza', 'type': 'armor', 'icon': 'G', 'sprite': 'assets/items/armor/gold_chestplate.png', 'stackable': False},
    'gold_gloves': {
    'name': 'Oro guantes', 'type': 'armor', 'icon': 'G', 'sprite': 'assets/items/armor/gold_gloves.png', 'stackable': False},
    'gold_hammer': {
    'name': 'Oro martillo', 'type': 'tool', 'icon': 'G', 'sprite': 'assets/items/tools/gold_hammer.png', 'stackable': False, 'tool_type': 'hammer'},
    'gold_helmet': {
    'name': 'Oro yelmo', 'type': 'armor', 'icon': 'G', 'sprite': 'assets/items/armor/gold_helmet.png', 'stackable': False},
    'gold_ingot': {
    'name': 'Oro lingote', 'type': 'resource', 'icon': 'G', 'sprite': 'assets/items/resources/gold_ingot.png', 'stackable': True},
    'gold_key': {
    'name': 'Oro llave', 'type': 'key', 'icon': 'G', 'sprite': 'assets/items/keys/gold_key.png', 'stackable': True},
    'gold_ore': {
    'name': 'Oro mineral', 'type': 'resource', 'icon': 'G', 'sprite': 'assets/items/resources/gold_ore.png', 'stackable': True},
    'gold_pants': {
    'name': 'Oro pantalones', 'type': 'armor', 'icon': 'G', 'sprite': 'assets/items/armor/gold_pants.png', 'stackable': False},
    'gold_pickaxe': {
    'name': 'Oro pico', 'type': 'tool', 'icon': 'G', 'sprite': 'assets/items/tools/gold_pickaxe.png', 'stackable': False, 'tool_type': 'axe'},
    'gold_shovel': {
    'name': 'Oro pala', 'type': 'tool', 'icon': 'G', 'sprite': 'assets/items/tools/gold_shovel.png', 'stackable': False, 'tool_type': 'shovel'},
    'gold_spear': {
    'name': 'Oro lanza', 'type': 'weapon', 'icon': 'G', 'sprite': 'assets/items/weapons/gold_spear.png', 'stackable': False},
    'gold_sword': {
    'name': 'Oro espada', 'type': 'weapon', 'icon': 'G', 'sprite': 'assets/items/weapons/gold_sword.png', 'stackable': False},
    'green_book': {
    'name': 'Verde libro', 'type': 'book', 'icon': 'G', 'sprite': 'assets/items/books_scrolls/green_book.png', 'stackable': True},
    'hammer_axe': {
    'name': 'Martillo hacha', 'type': 'tool', 'icon': 'H', 'sprite': 'assets/items/tools/hammer_axe.png', 'stackable': False, 'tool_type': 'axe'},
    'hoe': {
    'name': 'Azada', 'type': 'tool', 'icon': 'H', 'sprite': 'assets/items/tools/hoe.png', 'stackable': False, 'tool_type': 'hoe'},
    'iron': {
    'name': 'Hierro', 'type': 'resource', 'icon': 'I', 'sprite': 'assets/items/resources/iron.png', 'stackable': True},
    'iron_axe': {
    'name': 'Hierro hacha', 'type': 'tool', 'icon': 'I', 'sprite': 'assets/items/tools/iron_axe.png', 'stackable': False, 'tool_type': 'axe'},
    'iron_boots': {
    'name': 'Hierro botas', 'type': 'armor', 'icon': 'I', 'sprite': 'assets/items/armor/iron_boots.png', 'stackable': False},
    'iron_chestplate': {
    'name': 'Hierro coraza', 'type': 'armor', 'icon': 'I', 'sprite': 'assets/items/armor/iron_chestplate.png', 'stackable': False},
    'iron_gloves': {
    'name': 'Hierro guantes', 'type': 'armor', 'icon': 'I', 'sprite': 'assets/items/armor/iron_gloves.png', 'stackable': False},
    'iron_hammer': {
    'name': 'Hierro martillo', 'type': 'tool', 'icon': 'I', 'sprite': 'assets/items/tools/iron_hammer.png', 'stackable': False, 'tool_type': 'hammer'},
    'iron_helmet': {
    'name': 'Hierro yelmo', 'type': 'armor', 'icon': 'I', 'sprite': 'assets/items/armor/iron_helmet.png', 'stackable': False},
    'iron_ingot': {
    'name': 'Hierro lingote', 'type': 'resource', 'icon': 'I', 'sprite': 'assets/items/resources/iron_ingot.png', 'stackable': True},
    'iron_ore': {
    'name': 'Hierro mineral', 'type': 'resource', 'icon': 'I', 'sprite': 'assets/items/resources/iron_ore.png', 'stackable': True},
    'iron_pants': {
    'name': 'Hierro pantalones', 'type': 'armor', 'icon': 'I', 'sprite': 'assets/items/armor/iron_pants.png', 'stackable': False},
    'iron_pickaxe': {
    'name': 'Hierro pico', 'type': 'tool', 'icon': 'I', 'sprite': 'assets/items/tools/iron_pickaxe.png', 'stackable': False, 'tool_type': 'axe'},
    'iron_shovel': {
    'name': 'Hierro pala', 'type': 'tool', 'icon': 'I', 'sprite': 'assets/items/tools/iron_shovel.png', 'stackable': False, 'tool_type': 'shovel'},
    'iron_spear': {
    'name': 'Hierro lanza', 'type': 'weapon', 'icon': 'I', 'sprite': 'assets/items/weapons/iron_spear.png', 'stackable': False},
    'iron_sword': {
    'name': 'Hierro espada', 'type': 'weapon', 'icon': 'I', 'sprite': 'assets/items/weapons/iron_sword.png', 'stackable': False},
    'large_health_potion': {
    'name': 'Grande salud poción', 'type': 'potion', 'icon': 'L', 'sprite': 'assets/items/potions/large_health_potion.png', 'stackable': True},
    'large_mana_potion': {
    'name': 'Grande maná poción', 'type': 'potion', 'icon': 'L', 'sprite': 'assets/items/potions/large_mana_potion.png', 'stackable': True},
    'lava_core': {
    'name': 'Nucleo de lava', 'type': 'resource', 'icon': 'N', 'stackable': True},
    'leather_boots': {
    'name': 'Cuero botas', 'type': 'armor', 'icon': 'L', 'sprite': 'assets/items/armor/leather_boots.png', 'stackable': False},
    'leather_cap': {
    'name': 'Cuero gorra', 'type': 'armor', 'icon': 'L', 'sprite': 'assets/items/armor/leather_cap.png', 'stackable': False},
    'leather_gloves': {
    'name': 'Cuero guantes', 'type': 'armor', 'icon': 'L', 'sprite': 'assets/items/armor/leather_gloves.png', 'stackable': False},
    'leather_pants': {
    'name': 'Cuero pantalones', 'type': 'armor', 'icon': 'L', 'sprite': 'assets/items/armor/leather_pants.png', 'stackable': False},
    'leather_tunic': {
    'name': 'Cuero túnica', 'type': 'armor', 'icon': 'L', 'sprite': 'assets/items/armor/leather_tunic.png', 'stackable': False},
    'log': {
    'name': 'Tronco', 'type': 'resource', 'icon': 'L', 'sprite': 'assets/items/resources/log.png', 'stackable': True},
    'marine_iron': {
    'name': 'Hierro marino', 'type': 'resource', 'icon': 'H', 'stackable': True},
    'meat': {
    'name': 'Carne', 'type': 'food', 'icon': 'M', 'sprite': 'assets/items/food/meat.png', 'stackable': True},
    'molten_axe': {
    'name': 'Fundido hacha', 'type': 'tool', 'icon': 'M', 'sprite': 'assets/items/tools/molten_axe.png', 'stackable': False, 'tool_type': 'axe'},
    'molten_boots': {
    'name': 'Fundido botas', 'type': 'armor', 'icon': 'M', 'sprite': 'assets/items/armor/molten_boots.png', 'stackable': False},
    'molten_chestplate': {
    'name': 'Fundido coraza', 'type': 'armor', 'icon': 'M', 'sprite': 'assets/items/armor/molten_chestplate.png', 'stackable': False},
    'molten_gloves': {
    'name': 'Fundido guantes', 'type': 'armor', 'icon': 'M', 'sprite': 'assets/items/armor/molten_gloves.png', 'stackable': False},
    'molten_hammer': {
    'name': 'Fundido martillo', 'type': 'tool', 'icon': 'M', 'sprite': 'assets/items/tools/molten_hammer.png', 'stackable': False, 'tool_type': 'hammer'},
    'molten_helmet': {
    'name': 'Fundido yelmo', 'type': 'armor', 'icon': 'M', 'sprite': 'assets/items/armor/molten_helmet.png', 'stackable': False},
    'molten_ingot': {
    'name': 'Fundido lingote', 'type': 'resource', 'icon': 'M', 'sprite': 'assets/items/resources/molten_ingot.png', 'stackable': True},
    'molten_ore': {
    'name': 'Fundido mineral', 'type': 'resource', 'icon': 'M', 'sprite': 'assets/items/resources/molten_ore.png', 'stackable': True},
    'molten_pants': {
    'name': 'Fundido pantalones', 'type': 'armor', 'icon': 'M', 'sprite': 'assets/items/armor/molten_pants.png', 'stackable': False},
    'molten_pickaxe': {
    'name': 'Fundido pico', 'type': 'tool', 'icon': 'M', 'sprite': 'assets/items/tools/molten_pickaxe.png', 'stackable': False, 'tool_type': 'axe'},
    'molten_shovel': {
    'name': 'Fundido pala', 'type': 'tool', 'icon': 'M', 'sprite': 'assets/items/tools/molten_shovel.png', 'stackable': False, 'tool_type': 'shovel'},
    'molten_spear': {
    'name': 'Fundido lanza', 'type': 'weapon', 'icon': 'M', 'sprite': 'assets/items/weapons/molten_spear.png', 'stackable': False},
    'molten_sword': {
    'name': 'Fundido espada', 'type': 'weapon', 'icon': 'M', 'sprite': 'assets/items/weapons/molten_sword.png', 'stackable': False},
    'mushroom': {
    'name': 'Seta', 'type': 'food', 'icon': 'M', 'sprite': 'assets/items/food/mushroom.png', 'stackable': True},
    'obsidian': {
    'name': 'Obsidiana', 'type': 'resource', 'icon': 'O', 'stackable': True},
    'old_book': {
    'name': 'Viejo libro', 'type': 'book', 'icon': 'O', 'sprite': 'assets/items/books_scrolls/old_book.png', 'stackable': True},
    'old_mechanism': {
    'name': 'Mecanismo antiguo', 'type': 'resource', 'icon': 'M', 'stackable': True},
    'pickaxe': {
    'name': 'Pico', 'type': 'tool', 'icon': 'P', 'sprite': 'assets/items/tools/pickaxe.png', 'stackable': False, 'tool_type': 'axe'},
    'plank': {
    'name': 'Tabla', 'type': 'resource', 'icon': 'P', 'sprite': 'assets/items/resources/plank.png', 'stackable': True},
    'red_feathered_arrow': {
    'name': 'Roja emplumada flecha', 'type': 'ammo', 'icon': 'R', 'sprite': 'assets/items/ammo/red_feathered_arrow.png', 'stackable': True},
    'red_scroll': {
    'name': 'Roja pergamino', 'type': 'book', 'icon': 'R', 'sprite': 'assets/items/books_scrolls/red_scroll.png', 'stackable': True},
    'regular_health_potion': {
    'name': 'Normal salud poción', 'type': 'potion', 'icon': 'R', 'sprite': 'assets/items/potions/regular_health_potion.png', 'stackable': True},
    'regular_mana_potion': {
    'name': 'Normal maná poción', 'type': 'potion', 'icon': 'R', 'sprite': 'assets/items/potions/regular_mana_potion.png', 'stackable': True},
    'rope': {
    'name': 'Cuerda', 'type': 'resource', 'icon': 'R', 'stackable': True},
    'round_shield': {
    'name': 'Redondo escudo', 'type': 'shield', 'icon': 'R', 'sprite': 'assets/items/shields/round_shield.png', 'stackable': False},
    'ruby': {
    'name': 'Rubí', 'type': 'gem', 'icon': 'R', 'sprite': 'assets/items/gems/ruby.png', 'stackable': True},
    'ruby_ring': {
    'name': 'Rubí anillo', 'type': 'ring', 'icon': 'R', 'sprite': 'assets/items/rings/ruby_ring.png', 'stackable': False},
    'rum': {
    'name': 'Ron', 'type': 'resource', 'icon': 'R', 'stackable': True},
    'salt_stone': {
    'name': 'Piedra salina', 'type': 'resource', 'icon': 'L', 'stackable': True},
    'sapphire': {
    'name': 'Zafiro', 'type': 'gem', 'icon': 'S', 'sprite': 'assets/items/gems/sapphire.png', 'stackable': True},
    'sapphire_ring': {
    'name': 'Zafiro anillo', 'type': 'ring', 'icon': 'S', 'sprite': 'assets/items/rings/sapphire_ring.png', 'stackable': False},
    'sea_fiber': {
    'name': 'Fibra marina', 'type': 'resource', 'icon': 'F', 'stackable': True},
    'sealed_crate': {
    'name': 'Caja sellada', 'type': 'resource', 'icon': 'X', 'stackable': True},
    'seaweed': {
    'name': 'Alga', 'type': 'resource', 'icon': 'A', 'stackable': True},
    'shell': {
    'name': 'Concha', 'type': 'resource', 'icon': 'C', 'stackable': True},
    'silver_key': {
    'name': 'Plata llave', 'type': 'key', 'icon': 'S', 'sprite': 'assets/items/keys/silver_key.png', 'stackable': True},
    'simple_staff': {
    'name': 'Simple bastón', 'type': 'weapon', 'icon': 'S', 'sprite': 'assets/items/weapons/simple_staff.png', 'stackable': False},
    'small_empty_potion': {
    'name': 'Pequeña vacía poción', 'type': 'potion', 'icon': 'S', 'sprite': 'assets/items/potions/small_empty_potion.png', 'stackable': True},
    'small_health_potion': {
    'name': 'Pequeña salud poción', 'type': 'potion', 'icon': 'S', 'sprite': 'assets/items/potions/small_health_potion.png', 'stackable': True},
    'small_mana_potion': {
    'name': 'Pequeña maná poción', 'type': 'potion', 'icon': 'S', 'sprite': 'assets/items/potions/small_mana_potion.png', 'stackable': True},
    'steel_axe': {
    'name': 'Acero hacha', 'type': 'tool', 'icon': 'S', 'sprite': 'assets/items/tools/steel_axe.png', 'stackable': False, 'tool_type': 'axe'},
    'steel_boots': {
    'name': 'Acero botas', 'type': 'armor', 'icon': 'S', 'sprite': 'assets/items/armor/steel_boots.png', 'stackable': False},
    'steel_chestplate': {
    'name': 'Acero coraza', 'type': 'armor', 'icon': 'S', 'sprite': 'assets/items/armor/steel_chestplate.png', 'stackable': False},
    'steel_gloves': {
    'name': 'Acero guantes', 'type': 'armor', 'icon': 'S', 'sprite': 'assets/items/armor/steel_gloves.png', 'stackable': False},
    'steel_hammer': {
    'name': 'Acero martillo', 'type': 'tool', 'icon': 'S', 'sprite': 'assets/items/tools/steel_hammer.png', 'stackable': False, 'tool_type': 'hammer'},
    'steel_helmet': {
    'name': 'Acero yelmo', 'type': 'armor', 'icon': 'S', 'sprite': 'assets/items/armor/steel_helmet.png', 'stackable': False},
    'steel_ingot': {
    'name': 'Acero lingote', 'type': 'resource', 'icon': 'S', 'sprite': 'assets/items/resources/steel_ingot.png', 'stackable': True},
    'steel_ore': {
    'name': 'Acero mineral', 'type': 'resource', 'icon': 'S', 'sprite': 'assets/items/resources/steel_ore.png', 'stackable': True},
    'steel_pants': {
    'name': 'Acero pantalones', 'type': 'armor', 'icon': 'S', 'sprite': 'assets/items/armor/steel_pants.png', 'stackable': False},
    'steel_pickaxe': {
    'name': 'Acero pico', 'type': 'tool', 'icon': 'S', 'sprite': 'assets/items/tools/steel_pickaxe.png', 'stackable': False, 'tool_type': 'axe'},
    'steel_shovel': {
    'name': 'Acero pala', 'type': 'tool', 'icon': 'S', 'sprite': 'assets/items/tools/steel_shovel.png', 'stackable': False, 'tool_type': 'shovel'},
    'steel_spear': {
    'name': 'Acero lanza', 'type': 'weapon', 'icon': 'S', 'sprite': 'assets/items/weapons/steel_spear.png', 'stackable': False},
    'steel_sword': {
    'name': 'Acero espada', 'type': 'weapon', 'icon': 'S', 'sprite': 'assets/items/weapons/steel_sword.png', 'stackable': False},
    'stick': {
    'name': 'Palo', 'type': 'resource', 'icon': 'S', 'sprite': 'assets/items/resources/stick.png', 'stackable': True},
    'stone': {
    'name': 'Piedra', 'type': 'resource', 'icon': 'S', 'sprite': 'assets/items/resources/stone.png', 'stackable': True},
    'supplies': {
    'name': 'Provisiones', 'type': 'resource', 'icon': 'V', 'stackable': True},
    'tattered_wizard_hat': {
    'name': 'Raído wizard sombrero', 'type': 'armor', 'icon': 'T', 'sprite': 'assets/items/armor/tattered_wizard_hat.png', 'stackable': False},
    'topaz': {
    'name': 'Topacio', 'type': 'gem', 'icon': 'T', 'sprite': 'assets/items/gems/topaz.png', 'stackable': True},
    'topaz_ring': {
    'name': 'Topacio anillo', 'type': 'ring', 'icon': 'T', 'sprite': 'assets/items/rings/topaz_ring.png', 'stackable': False},
    'treasure': {
    'name': 'Tesoro', 'type': 'resource', 'icon': 'T', 'stackable': True},
    'triangle_shield': {
    'name': 'Triangular escudo', 'type': 'shield', 'icon': 'T', 'sprite': 'assets/items/shields/triangle_shield.png', 'stackable': False},
    'watering_can': {
    'name': 'Regadera', 'type': 'ring', 'icon': 'W', 'sprite': 'assets/items/rings/watering_can.png', 'stackable': False},
    'wizard_hat': {
    'name': 'Wizard sombrero', 'type': 'armor', 'icon': 'W', 'sprite': 'assets/items/armor/wizard_hat.png', 'stackable': False},
    'wood': {
    'name': 'Madera', 'type': 'resource', 'icon': 'W', 'sprite': 'assets/items/resources/wood.png', 'stackable': True},
    'wood_floor': {
    'name': 'Suelo de madera', 'type': 'placeable', 'icon': 'W', 'sprite': 'assets/items/building/wood_floor.png', 'stackable': True},
    'wooden_hammer': {
    'name': 'Madera martillo', 'type': 'tool', 'icon': 'W', 'sprite': 'assets/items/tools/wooden_hammer.png', 'stackable': False, 'tool_type': 'hammer'},
    'wooden_pickaxe': {
    'name': 'Madera pico', 'type': 'tool', 'icon': 'W', 'sprite': 'assets/items/tools/wooden_pickaxe.png', 'stackable': False, 'tool_type': 'axe'},
    'wooden_shovel': {
    'name': 'Madera pala', 'type': 'tool', 'icon': 'W', 'sprite': 'assets/items/tools/wooden_shovel.png', 'stackable': False, 'tool_type': 'shovel'},
    'wooden_spear': {
    'name': 'Madera lanza', 'type': 'weapon', 'icon': 'W', 'sprite': 'assets/items/weapons/wooden_spear.png', 'stackable': False},
    'wooden_sword': {
    'name': 'Madera espada', 'type': 'weapon', 'icon': 'W', 'sprite': 'assets/items/weapons/wooden_sword.png', 'stackable': False}
}


def get_item_data(item_id):
    return ITEM_DATABASE.get(item_id)


def is_item_stackable(item_id):
    item_data = get_item_data(item_id)

    if item_data is None:
        return False

    return item_data.get("stackable", True)


def get_item_max_stack(item_id):
    item_data = get_item_data(item_id)

    if item_data is None:
        return 0

    if not item_data.get("stackable", True):
        return DEFAULT_UNSTACKABLE_MAX_STACK

    return item_data.get("max_stack", DEFAULT_STACKABLE_MAX_STACK)
