"""실제 SDL 이미지와 모드 스택을 사용하는 통합 테스트. GUI 창은 표시하지 않는다."""

import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pico2d as p
import pico2d.pico2d as backend
import boy as boy_module
import game_framework as framework
import game_world as world
import item_mode
import logo_mode
import pause_mode
import play_mode
import title_mode
from ball import Ball
from items import Item


def key(symbol, kind=p.SDL_KEYDOWN):
    return SimpleNamespace(type=kind, key=symbol)


def dispatch(mode, *events):
    with patch.object(mode, 'get_events', return_value=list(events)):
        mode.handle_events()


def snapshot():
    return [(id(obj), getattr(obj, 'x', None), getattr(obj, 'y', None),
             getattr(obj, 'frame', None)) for layer in world.world for obj in layer]


class ModeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p.open_canvas()
        # Pico2D는 dummy 드라이버에서 빈 렌더러 포인터를 None으로 인식하지 못한다.
        if not backend.renderer:
            backend.renderer = backend.SDL_CreateRenderer(
                backend.window, -1, backend.SDL_RENDERER_SOFTWARE)
        if not backend.renderer:
            p.close_canvas()
            raise RuntimeError('SDL 소프트웨어 렌더러를 만들 수 없습니다.')

    @classmethod
    def tearDownClass(cls):
        Ball.images.clear()
        p.close_canvas()

    def setUp(self):
        self.clock = 100.0
        for module in (play_mode, boy_module, logo_mode):
            timer = patch.object(module, 'get_time', side_effect=lambda: self.clock)
            timer.start()
            self.addCleanup(timer.stop)
        framework.running = True
        framework.stack = []
        framework.change_mode(play_mode)

    def tearDown(self):
        while framework.stack:
            framework.stack.pop().finish()
        framework.running = False
        self.assertTrue(all(not layer for layer in world.world))

    def open_items(self):
        dispatch(play_mode, key(p.SDLK_i))
        self.assertEqual(framework.stack, [play_mode, item_mode])

    def test_logo_title_play_flow(self):
        framework.change_mode(logo_mode)
        self.clock += 1.9
        logo_mode.update()
        self.assertIs(framework.stack[-1], logo_mode)
        self.clock += 0.2
        logo_mode.update()
        self.assertEqual(framework.stack, [title_mode])
        dispatch(title_mode, key(p.SDLK_SPACE))
        self.assertEqual(framework.stack, [play_mode])

    def test_all_number_keys_and_selection_persistence(self):
        self.open_items()
        for symbol, expected in item_mode.ITEM_KEYS.items():
            with self.subTest(symbol=symbol):
                dispatch(item_mode, key(symbol))
                self.assertEqual(play_mode.boy.selected_item, expected)
                item_mode.render()
        dispatch(item_mode, key(p.SDLK_i))
        self.open_items()
        self.assertEqual(play_mode.boy.selected_item, Item.LARGE_BALL)

    def test_default_small_ball_fires_without_opening_items(self):
        self.assertEqual(play_mode.boy.selected_item, Item.SMALL_BALL)
        dispatch(play_mode, key(p.SDLK_SPACE))
        ball = world.world[1][-1]
        self.assertIsInstance(ball, Ball)
        self.assertEqual(ball.item, Item.SMALL_BALL)
        self.open_items()
        dispatch(item_mode, key(p.SDLK_i))
        dispatch(play_mode, key(p.SDLK_SPACE))
        self.assertEqual(world.world[1][-1].item, Item.SMALL_BALL)
        self.assertEqual(len(world.world[1]), 3)

    def test_ball_sizes_and_none(self):
        self.open_items()
        dispatch(item_mode, key(p.SDLK_0), key(p.SDLK_i))
        dispatch(play_mode, key(p.SDLK_SPACE))
        self.assertEqual(len(world.world[1]), 1)
        self.open_items()
        # 제공된 PNG는 가장자리 여백을 포함해 각각 23×23, 43×43이다.
        for symbol, expected_size in ((p.SDLK_1, 23), (p.SDLK_2, 43)):
            dispatch(item_mode, key(symbol), key(p.SDLK_i))
            dispatch(play_mode, key(p.SDLK_SPACE))
            ball = world.world[1][-1]
            self.assertIsInstance(ball, Ball)
            self.assertEqual((ball.image.w, ball.image.h), (expected_size, expected_size))
            play_mode.render()
            self.open_items()
        existing = list(world.world[1])
        dispatch(item_mode, key(p.SDLK_0), key(p.SDLK_i))
        dispatch(play_mode, key(p.SDLK_SPACE))
        self.assertEqual(world.world[1], existing)
        self.assertEqual([ball.image.w for ball in existing[1:]], [23, 43])

    def test_item_mode_freezes_world_and_resumes_same_objects(self):
        play_mode.boy.select_item(Item.SMALL_BALL)
        dispatch(play_mode, key(p.SDLK_RIGHT), key(p.SDLK_SPACE))
        play_mode.update()
        before = snapshot()
        self.open_items()
        for _ in range(5):
            self.clock += 10
            framework.stack[-1].update()
            framework.stack[-1].render()
        self.assertEqual(snapshot(), before)
        dispatch(item_mode, key(p.SDLK_i))
        self.assertEqual(snapshot(), before)
        play_mode.update()
        self.assertNotEqual(snapshot(), before)

    def test_idle_sleep_timer_excludes_item_mode(self):
        self.clock += 4
        play_mode.update()
        self.open_items()
        self.clock += 120
        dispatch(item_mode, key(p.SDLK_i))
        play_mode.update()
        self.assertEqual(play_mode.boy.state, 'IDLE')
        self.clock += 1.1
        play_mode.update()
        self.assertEqual(play_mode.boy.state, 'SLEEP')

    def test_key_release_during_item_mode(self):
        dispatch(play_mode, key(p.SDLK_RIGHT))
        self.open_items()
        before = snapshot()
        dispatch(item_mode, key(p.SDLK_RIGHT, p.SDL_KEYUP))
        self.assertEqual(snapshot(), before)
        dispatch(item_mode, key(p.SDLK_i))
        self.assertEqual(play_mode.boy.state, 'IDLE')
        self.assertFalse(play_mode.boy.pressed_keys)

    def test_key_releases_in_transition_event_batches(self):
        for symbol, mode in ((p.SDLK_i, item_mode), (p.SDLK_p, pause_mode)):
            for release_on_entry in (True, False):
                with self.subTest(mode=mode.__name__, entry=release_on_entry):
                    dispatch(play_mode, key(p.SDLK_RIGHT))
                    release = key(p.SDLK_RIGHT, p.SDL_KEYUP)
                    dispatch(play_mode, *([key(symbol), release] if release_on_entry else [key(symbol)]))
                    dispatch(mode, *([key(symbol)] if release_on_entry else [key(symbol), release]))
                    self.assertEqual(framework.stack, [play_mode])
                    self.assertFalse(play_mode.boy.pressed_keys)
                    self.assertEqual(play_mode.boy.state, 'IDLE')

    def test_repeated_entry_preserves_selection_and_layer_counts(self):
        original_boy = play_mode.boy
        for index in range(10):
            self.open_items()
            dispatch(item_mode, key(p.SDLK_2), key(p.SDLK_i))
            self.assertIs(play_mode.boy, original_boy)
            self.assertEqual(play_mode.boy.selected_item, Item.LARGE_BALL)
            self.assertEqual([len(layer) for layer in world.world], [1, 1, 0])
            dispatch(play_mode, key(p.SDLK_p))
            pause_mode.render()
            dispatch(pause_mode, key(p.SDLK_p))
            self.assertEqual(framework.stack, [play_mode])

    def test_invalid_keys_do_not_change_selection_or_move_world(self):
        self.open_items()
        before = snapshot()
        dispatch(item_mode, key(p.SDLK_9), key(p.SDLK_p), key(p.SDLK_SPACE), key(p.SDLK_LEFT))
        item_mode.update()
        self.assertEqual(play_mode.boy.selected_item, Item.SMALL_BALL)
        self.assertEqual(snapshot(), before)
        self.assertEqual(framework.stack, [play_mode, item_mode])

    def test_escape_from_items_returns_to_title_and_cleans_world(self):
        self.open_items()
        dispatch(item_mode, key(p.SDLK_ESCAPE))
        self.assertEqual(framework.stack, [title_mode])
        self.assertTrue(all(not layer for layer in world.world))
        dispatch(title_mode, key(p.SDLK_SPACE))
        self.assertEqual(play_mode.boy.selected_item, Item.SMALL_BALL)

    def test_window_close_from_items_requests_quit(self):
        self.open_items()
        dispatch(item_mode, SimpleNamespace(type=p.SDL_QUIT))
        self.assertFalse(framework.running)

    def test_sleeping_character_selection_and_wake_up(self):
        self.clock += 6
        play_mode.update()
        self.assertEqual(play_mode.boy.state, 'SLEEP')
        self.open_items()
        dispatch(item_mode, key(p.SDLK_2))
        item_mode.render()
        dispatch(item_mode, key(p.SDLK_i))
        self.assertEqual(play_mode.boy.state, 'SLEEP')
        dispatch(play_mode, key(p.SDLK_SPACE))
        self.assertEqual(play_mode.boy.state, 'IDLE')
        self.assertEqual(len(world.world[1]), 1)
        dispatch(play_mode, key(p.SDLK_SPACE))
        self.assertEqual(world.world[1][-1].item, Item.LARGE_BALL)

    def test_main_loop_handles_complete_mode_sequence(self):
        while framework.stack:
            framework.stack.pop().finish()
        steps = iter([
            (logo_mode, []),
            (title_mode, [key(p.SDLK_SPACE)]),
            (play_mode, [key(p.SDLK_i)]),
            (item_mode, [key(p.SDLK_2), key(p.SDLK_i)]),
            (play_mode, [key(p.SDLK_SPACE), key(p.SDLK_p)]),
            (pause_mode, [key(p.SDLK_p)]),
            (play_mode, [key(p.SDLK_ESCAPE)]),
            (title_mode, [key(p.SDLK_ESCAPE)]),
        ])

        def next_events():
            expected_mode, events = next(steps)
            self.assertIs(framework.stack[-1], expected_mode)
            self.clock += 3
            return events

        patches = [patch.object(module, 'get_events', side_effect=next_events)
                   for module in (logo_mode, title_mode, play_mode, item_mode, pause_mode)]
        for event_patch in patches:
            event_patch.start()
            self.addCleanup(event_patch.stop)
        with patch.object(framework.time, 'sleep'):
            framework.run(logo_mode)
        self.assertEqual(framework.stack, [])
        self.assertFalse(framework.running)


if __name__ == '__main__':
    unittest.main()
