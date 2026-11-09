from pico2d import *

import game_framework
import game_world
import play_mode
import title_mode


def init():
    pass


def finish():
    pass


def handle_events():
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_p:
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
    x, y = get_canvas_width() // 2, get_canvas_height() - 45
    draw_rectangle(x - 30, y - 25, x + 30, y + 25, 0, 0, 0, filled=True)
    draw_rectangle(x - 16, y - 15, x - 6, y + 15, 255, 255, 255, filled=True)
    draw_rectangle(x + 6, y - 15, x + 16, y + 15, 255, 255, 255, filled=True)
    update_canvas()


def pause():
    pass


def resume():
    pass
