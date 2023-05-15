import pygame as pg

from collections import deque
from pygame.math import Vector2 as v2

from source.gamestate import GameState
from source.globals   import *
from source.util      import draw_grid

class Game(GameState):

	def update(self):
		if self.accepting_inputs:
			if self.game_runner.player_inputs[PlayerInput.ESCAPE]:
				self.accepting_inputs = False
				self.is_updating      = False
				self.is_drawing       = True
				self.game_runner.states[GameStateNum.PAUSE].accepting_inputs = True
				self.game_runner.states[GameStateNum.PAUSE].is_updating      = True
				self.game_runner.states[GameStateNum.PAUSE].is_drawing       = True
				self.game_runner.player_inputs[PlayerInput.ESCAPE] = False	# clear keypress so other states don't use it
		#
		if self.is_updating:
			pass

	def draw(self):
		screen = self.game_runner.screen
		offset = self.game_runner.camera_pos
		if self.is_drawing:
			grid_offset = v2(offset.x % (2*GRID_SIZE), offset.y % (2*GRID_SIZE))
			draw_grid(screen, RES,   GRID_SIZE, grid_offset, Color.GRID_MINOR)
			draw_grid(screen, RES, 2*GRID_SIZE, grid_offset, Color.GRID_MAJOR)
			self.game_runner.fonts['large_w'].render(screen, "main game loop", v2(5,4), centered=False)

	def reset(self):
		self.accepting_inputs = True
		self.is_updating      = True
		self.is_drawing       = True
		