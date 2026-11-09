from pathlib import Path

from pico2d import get_canvas_width, load_image

import game_world
from items import Item, ITEM_IMAGE_FILES


class Ball:
    images = {}

    def __init__(self, x, y, velocity, item=Item.SMALL_BALL):
        self.item = Item(item)
        if self.item == Item.NONE:
            raise ValueError('아이템 없음으로는 공을 만들 수 없습니다.')
        if self.item not in Ball.images:
            path = Path(__file__).resolve().parent / ITEM_IMAGE_FILES[self.item]
            Ball.images[self.item] = load_image(str(path))
        self.image = Ball.images[self.item]
        self.x, self.y = x, y
        self.velocity = velocity

    def update(self):
        self.x += self.velocity
        if self.x < 0 or self.x > get_canvas_width():
            game_world.remove_object(self)

    def draw(self):
        self.image.draw(self.x, self.y)
