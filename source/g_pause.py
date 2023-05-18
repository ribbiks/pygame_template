import pygame as pg

from collections import deque
from pygame.math import Vector2 as v2

from source.gamestate import GameState
from source.globals   import *


class PauseMenu(GameState):

    def __init__(self, game_runner):
        super().__init__(game_runner)
        self.pause_fade = pg.Surface(game_runner.screen.get_size())
        self.pause_fade.fill(Color.BLACK)
        self.pause_fade.set_alpha(128)

    def update(self):
        if self.accepting_inputs:
            if self.game_runner.player_inputs[PlayerInput.ESCAPE]:
                self.accepting_inputs = False
                self.is_updating      = False
                self.is_drawing       = False
                self.game_runner.states[GameStateNum.GAME].accepting_inputs = True
                self.game_runner.states[GameStateNum.GAME].is_updating      = True
                self.game_runner.states[GameStateNum.GAME].is_drawing       = True
                self.game_runner.player_inputs[PlayerInput.ESCAPE] = False  # clear keypress so other states don't use it
        #
        if self.is_updating:
            pass

    def draw(self):
        screen = self.game_runner.screen
        offset = self.game_runner.camera_pos
        if self.is_drawing:
            screen.blit(self.pause_fade, (0,0), special_flags=pg.BLEND_ALPHA_SDL2)
            self.game_runner.fonts['large_w'].render(screen, "pause menu!", v2(5,20), centered=False)

    def reset(self):
        self.accepting_inputs = False
        self.is_updating      = False
        self.is_drawing       = False
