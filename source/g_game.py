import pygame as pg

from collections import deque
from pygame.math import Vector2 as v2

from source.gamestate import GameState
from source.globals   import *
from source.util      import draw_grid


class Game(GameState):

    def update(self):
        if self.accepting_inputs:
            if self.game_runner.player_inputs[PlayerInput.ESCAPE] or self.game_runner.player_inputs[PlayerInput.START]:
                self.accepting_inputs = False
                self.is_updating      = False
                self.is_drawing       = True
                self.game_runner.states[GameStateNum.PAUSE].accepting_inputs = True
                self.game_runner.states[GameStateNum.PAUSE].is_updating      = True
                self.game_runner.states[GameStateNum.PAUSE].is_drawing       = True
                self.game_runner.player_inputs[PlayerInput.ESCAPE] = False  # clear keypress so other states don't use it
                self.game_runner.player_inputs[PlayerInput.START]  = False
        #
        if self.is_updating:
            self.game_runner.player_object.update(self.game_runner.input_buffer)
            camera_target = (1.0 - MOUSE_TARGET_WEIGHT)*self.game_runner.player_object.pos + MOUSE_TARGET_WEIGHT*self.game_runner.mouse_pos_map + v2(0,-8)
            camera_target = self.game_runner.player_object.pos
            self.game_runner.camera.set_target(camera_target)
            self.game_runner.camera.update()
            #print(self.game_runner.player_object.pos, self.game_runner.camera.pos)

    def draw(self):
        screen = self.game_runner.screen
        offset = self.game_runner.camera.pos
        if self.is_drawing:
            grid_offset = v2(offset.x % (2*GRID_SIZE), offset.y % (2*GRID_SIZE))
            draw_grid(screen, RES,   GRID_SIZE, grid_offset, Color.GRID_MINOR)
            draw_grid(screen, RES, 2*GRID_SIZE, grid_offset, Color.GRID_MAJOR)
            self.game_runner.fonts['large_w'].render(screen, "main game loop", v2(5,4), centered=False)
            self.game_runner.player_object.draw(screen, offset, state_draw_font=self.game_runner.fonts['small_w'])

    def reset(self):
        self.accepting_inputs = True
        self.is_updating      = True
        self.is_drawing       = True
