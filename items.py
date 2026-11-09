from enum import IntEnum


class Item(IntEnum):
    NONE = 0
    SMALL_BALL = 1
    LARGE_BALL = 2


ITEM_IMAGE_FILES = {
    Item.SMALL_BALL: 'ball21x21.png',
    Item.LARGE_BALL: 'ball41x41.png',
}

ITEM_NAMES = {
    Item.NONE: 'None',
    Item.SMALL_BALL: 'Small ball',
    Item.LARGE_BALL: 'Large ball',
}
