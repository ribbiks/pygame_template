import pygame as pg
import sys

from collections import deque
from pygame.math import Vector2 as v2

from source.gamestate import GameState
from source.globals   import *
from source.util      import draw_grid


class MainMenu(GameState):

    def update(self):
        if self.accepting_inputs:
            if self.game_runner.player_inputs[PlayerInput.ESCAPE]:
                pg.quit()
                sys.exit()
            if self.game_runner.player_inputs[PlayerInput.BUTTON_A]:
                self.game_runner.next_gamestate = [GameStateNum.SAVE_MENU]
                self.game_runner.trans_alpha    = deque(FADE_SEQUENCE)
                self.accepting_inputs = False

    def draw(self):
        screen = self.game_runner.screen
        offset = self.game_runner.camera.pos
        #
        grid_offset = v2(offset.x % (2*GRID_SIZE), offset.y % (2*GRID_SIZE))
        draw_grid(screen, RES,   GRID_SIZE, grid_offset, Color.GRID_MINOR)
        draw_grid(screen, RES, 2*GRID_SIZE, grid_offset, Color.GRID_MAJOR)
        #
        self.game_runner.fonts['large_w'].render(screen, "oh hey this is the main menu", v2(5,4), centered=False)

    def reset(self):
        self.accepting_inputs = True
        self.is_updating      = True
        self.is_drawing       = True
