from assets.bitmaps.tree_oak_bitmap import TREE_OAK_BITMAP


BITMAP_DATABASE = {
    "tree_oak": TREE_OAK_BITMAP,
}


def get_bitmap_data(bitmap_id):
    return BITMAP_DATABASE.get(bitmap_id)