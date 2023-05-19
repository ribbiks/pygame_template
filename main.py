#!/usr/bin/env python
# encoding: utf-8
import asyncio
import pygame as pg
import os
import pathlib
import platform

from collections import deque
from pygame.math import Vector2 as v2

from source.font       import Font
from source.geometry   import value_clamp
from source.globals    import *
from source.g_mainmenu import MainMenu
from source.g_game     import Game
from source.g_pause    import PauseMenu
from source.input      import get_input_args, InputManager
from source.player     import Player
from source.util       import draw_fullscreen_border

# are we making the web version?
PYGBAG = False
if platform.system().lower() == "emscripten":
    # Note that this stuff only resolves when running in a web context
    if __WASM__ and __EMSCRIPTEN__ and __EMSCRIPTEN__.is_browser:
        from __EMSCRIPTEN__ import window
    PYGBAG = True


class GameRunner:
    #
    #
    #
    def __init__(self, BASE_DIR, DISPLAY_NUM, SCALE_FACTOR, RUN_FULLSCREEN):
        #
        pg.init()
        pg.mixer.set_num_channels(12)
        pg.display.set_caption(GAME_VERS)
        #
        # DISPLAY STUFF:
        #
        # screen      = the main low-res screen object that everything will be blitted to
        # screen_out  = resized surface that is integer-scaled up. this is final output in windowed mode
        # screen_full = in fullscreen mode screen_out will be rendered in the center of this surface
        #
        self.screen      = pg.Surface(RES)
        self.screen_out  = None
        self.screen_full = None
        #
        self.fullscreen_offset = (0,0)
        self.is_fullscreen     = RUN_FULLSCREEN
        #
        if PYGBAG:
            scaled_res = (RES[0]*SCALE_FACTOR, RES[1]*SCALE_FACTOR)
            self.screen_out = pg.display.set_mode(size=scaled_res, flags=0, depth=0, display=DISPLAY_NUM, vsync=0)
        else:
            display_sizes = pg.display.get_desktop_sizes()
            if DISPLAY_NUM >= len(display_sizes) or DISPLAY_NUM < 0:
                print('Error: invalid display number')
                exit(1)
            my_display_size = display_sizes[DISPLAY_NUM]
            if SCALE_FACTOR <= 0:
                display_scale_factor = 1
                while RES[0]*(display_scale_factor+1) <= my_display_size[0] and RES[1]*(display_scale_factor+1) <= my_display_size[1]:
                    display_scale_factor += 1
            else:
                display_scale_factor = SCALE_FACTOR
            scaled_res = (RES[0]*display_scale_factor, RES[1]*display_scale_factor)
            if self.is_fullscreen:
                self.screen_full = pg.display.set_mode(size=my_display_size, flags=pg.FULLSCREEN, depth=0, display=DISPLAY_NUM, vsync=0)
                self.screen_out  = pg.Surface(scaled_res)
                fullscreen_size  = self.screen_full.get_size()
                self.fullscreen_offset = (int((fullscreen_size[0]-scaled_res[0])/2), int((fullscreen_size[1]-scaled_res[1])/2))
            else:
                # make room for top bar if needed (which is 30px on mac)
                if scaled_res[1] >= my_display_size[1] - 30:
                    scaled_res = (RES[0]*(display_scale_factor-1), RES[1]*(display_scale_factor-1))
                self.screen_out = pg.display.set_mode(size=scaled_res, flags=0, depth=0, display=DISPLAY_NUM, vsync=0)
        #
        self.trans_fade = pg.Surface(RES)
        self.trans_fade.fill(Color.BLACK)
        self.trans_alpha = deque()
        self.current_trans_alpha = 0
        #
        self.input_manager = InputManager()
        self.player_inputs = None
        self.player_object = Player(v2(128,128), 0)
        #
        self.camera_pos       = v2(0,0)
        self.mouse_pos_screen = v2(0,0)
        self.mouse_pos_map    = v2(0,0)
        #
        self.load_assets(BASE_DIR)
        #
        self.states = [MainMenu(self), Game(self), PauseMenu(self)]
        self.current_states = [GameStateNum.MAIN_MENU]
        self.next_gamestate = []
        #
        asyncio.run(self.main())

    #
    #
    #
    def load_assets(self, BASE_DIR):
        FONT_DIR = os.path.join(BASE_DIR, 'assets', 'font')
        #
        small_font = os.path.join(FONT_DIR, 'small_font.png')
        large_font = os.path.join(FONT_DIR, 'large_font.png')
        self.fonts = {'small_b': Font(small_font, Color.BLACK),
                      'small_w': Font(small_font, Color.WHITE),
                      'large_b': Font(large_font, Color.BLACK),
                      'large_w': Font(large_font, Color.WHITE)}

    #
    #
    #
    def get_inputs(self):
        pg_events = pg.event.get()
        self.player_inputs = self.input_manager.get_inputs_from_events(pg_events)
        print([1*n for n in self.player_inputs])
        #
        (mx,my) = pg.mouse.get_pos()
        upscaled_size    = self.screen_out.get_size()
        mouse_rescale    = (RES[0]/upscaled_size[0], RES[1]/upscaled_size[1])
        self.mouse_pos_screen = v2(value_clamp(int((mx-self.fullscreen_offset[0])*mouse_rescale[0] + 0.5), 0, RES[0]),
                                   value_clamp(int((my-self.fullscreen_offset[1])*mouse_rescale[1] + 0.5), 0, RES[1]))
        self.mouse_pos_map = self.mouse_pos_screen - self.camera_pos

    #
    #
    #
    def update(self):
        for s in self.current_states:
            self.states[s].update()
        #
        # handle state transitions
        #
        if self.next_gamestate:
            self.current_trans_alpha = self.trans_alpha.popleft()
            if self.current_trans_alpha >= 255:
                self.current_states = self.next_gamestate
                for s in self.current_states:
                    self.states[s].reset()
            if not self.trans_alpha:
                self.next_gamestate = []
                self.current_trans_alpha = 0

    #
    #
    #
    def draw(self):
        self.screen.fill(Color.BLACK)
        for s in self.current_states:
            self.states[s].draw()
        #
        # transition fade
        #
        if self.current_trans_alpha:
            self.trans_fade.set_alpha(self.current_trans_alpha)
            self.screen.blit(self.trans_fade, (0,0), special_flags=pg.BLEND_ALPHA_SDL2)
        #
        # debug widgets
        #
        fps_str = '{0} fps'.format(int(len(self.recent_frame_times)/sum(self.recent_frame_times) + 0.5))
        mxy_str = '{0}, {1}'.format(int(self.mouse_pos_map.x), int(self.mouse_pos_map.y))
        self.fonts['small_w'].render(self.screen, fps_str, v2(RES[0]-28, 4),         centered=False)
        self.fonts['small_w'].render(self.screen, mxy_str, v2(RES[0]-34, RES[1]-10), centered=False)
        #
        # final output to screen
        #
        scaled_screen = pg.transform.scale(self.screen, self.screen_out.get_size())
        if self.is_fullscreen:
            self.screen_full.fill(Color.BLACK)
            draw_fullscreen_border(self.screen_full, self.fullscreen_offset, self.screen_out.get_size())
            self.screen_full.blit(scaled_screen, self.fullscreen_offset)
        else:
            self.screen_out.blit(scaled_screen, (0,0))
        pg.display.update()

    #
    #
    #
    async def main(self):
        #
        dt = 1.0 / FRAMERATE
        current_time  = pg.time.get_ticks()/1000.
        accumulator   = 0.0
        max_accum     = MAX_UPDATE_FRAMES / FRAMERATE
        current_frame = 0
        self.recent_frame_times   = deque([current_time])
        self.previous_update_time = current_time
        #
        while True:
            await asyncio.sleep(0)
            #
            new_time     = pg.time.get_ticks()/1000.
            frame_time   = new_time - current_time
            current_time = new_time
            accumulator  = min(accumulator + frame_time, max_accum) # prevent spiral of death
            #
            if accumulator >= dt:
                self.get_inputs()
            while accumulator >= dt:
                self.update()
                self.recent_frame_times.append(pg.time.get_ticks()/1000. - self.previous_update_time)
                while len(self.recent_frame_times) > NUM_FRAMES_FOR_FPS:
                    self.recent_frame_times.popleft()
                self.previous_update_time = current_time
                accumulator -= dt
                current_frame += 1
            #if current_frame - prev_frame >= 1:
            #   print('updates:', current_frame - prev_frame)
            self.draw()


if __name__ == '__main__':
    try:
        if PYGBAG:
            [DISPLAY_NUM, SCALE_FACTOR, RUN_FULLSCREEN] = [0, 1, False]
            BASE_DIR = ''
        else:
            [DISPLAY_NUM, SCALE_FACTOR, RUN_FULLSCREEN] = get_input_args()
            BASE_DIR = pathlib.Path(__file__).resolve().parent
        game_runner = GameRunner(BASE_DIR, DISPLAY_NUM, SCALE_FACTOR, RUN_FULLSCREEN)
        game_runner.run()
    finally:
        pg.quit()
