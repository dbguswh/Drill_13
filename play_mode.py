from pico2d import *
import game_framework
import game_world
import item_mode
import pause_mode
import title_mode
from boy import Boy
from grass import Grass


def handle_events():
    event_list = get_events()
    for index, event in enumerate(event_list):
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.change_mode(title_mode)
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_p:
            game_framework.push_mode(pause_mode)
            remember_key_releases(event_list[index + 1:])
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_i:
            game_framework.push_mode(item_mode)
            remember_key_releases(event_list[index + 1:])
            return
        else:
            boy.handle_event(event)



def init():
    global boy


    boy = Boy()
    game_world.add_oject(boy)

    grass = Grass()
    game_world.add_oject(grass, 0)



def update():
    game_world.update()


def render():
    clear_canvas()
    game_world.render()
    update_canvas()

def finish():
    global boy
    game_world.clear()
    del boy


def pause():
    global pause_started_at, paused_key_up_events
    pause_started_at = get_time()
    paused_key_up_events = []


def remember_key_releases(events):
    paused_key_up_events.extend(event for event in events if event.type == SDL_KEYUP)


def resume():
    boy.idle_started_at += get_time() - pause_started_at
    for event in paused_key_up_events:
        boy.handle_event(event)
    paused_key_up_events.clear()
