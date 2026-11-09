from pathlib import Path

from pico2d import *

import game_framework
import game_world
import play_mode
import title_mode


def init():
    global panel
    panel = load_image(str(Path(__file__).resolve().parent / 'item_select.png'))


def finish():
    global panel
    del panel


def handle_events():
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_i:
            game_framework.pop_mode()
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.pop_mode()
            game_framework.change_mode(title_mode)
            return
        elif event.type == SDL_KEYUP:
            play_mode.paused_key_up_events.append(event)


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
