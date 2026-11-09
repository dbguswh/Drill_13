from pathlib import Path

from pico2d import *

import game_world


def init():
    global panel
    panel = load_image(str(Path(__file__).resolve().parent / 'item_select.png'))


def finish():
    global panel
    del panel


def handle_events():
    pass


def update():
    pass


def render():
    clear_canvas()
    game_world.render()
    panel.draw(get_canvas_width() / 2, get_canvas_height() / 2)
    update_canvas()


def pause():
    pass


def resume():
    pass
