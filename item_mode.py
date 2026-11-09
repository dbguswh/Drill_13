from pathlib import Path

import pico2d
from pico2d import *

import game_framework
import game_world
import play_mode
import title_mode
from items import Item, ITEM_NAMES


ITEM_KEYS = {
    SDLK_0: Item.NONE,
    SDLK_1: Item.SMALL_BALL,
    SDLK_2: Item.LARGE_BALL,
    SDLK_KP_0: Item.NONE,
    SDLK_KP_1: Item.SMALL_BALL,
    SDLK_KP_2: Item.LARGE_BALL,
}


def init():
    global panel, font
    panel = load_image(str(Path(__file__).resolve().parent / 'item_select.png'))
    font = load_font(str(Path(pico2d.__file__).resolve().parent / 'data' / 'ConsolaMalgun.ttf'), 18)


def finish():
    global panel, font
    del panel
    del font


def handle_events():
    events = get_events()
    for index, event in enumerate(events):
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_i:
            play_mode.remember_key_releases(events[index + 1:])
            game_framework.pop_mode()
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.pop_mode()
            game_framework.change_mode(title_mode)
            return
        elif event.type == SDL_KEYUP:
            play_mode.remember_key_releases([event])
        elif event.type == SDL_KEYDOWN and event.key in ITEM_KEYS:
            play_mode.boy.select_item(ITEM_KEYS[event.key])


def update():
    pass


def render():
    clear_canvas()
    game_world.render()
    x, y = get_canvas_width() / 2, get_canvas_height() / 2
    panel.draw(x, y)
    selected = play_mode.boy.selected_item
    row_y = y + 66 - int(selected) * 66
    draw_rectangle(x - 128, row_y - 28, x + 128, row_y + 28, 240, 155, 20)
    draw_rectangle(x - 127, row_y - 27, x + 127, row_y + 27, 240, 155, 20)
    draw_rectangle(x - 172, y - 172, x + 172, y - 122, 35, 35, 40, filled=True)
    font.draw(x - 156, y - 138, f'Selected: {ITEM_NAMES[selected]}', (255, 230, 160))
    font.draw(x - 156, y - 160, 'I: Back to play   ESC: Title', (255, 255, 255))
    update_canvas()


def pause():
    pass


def resume():
    pass
