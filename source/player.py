import pygame as pg

from pygame.math import Vector2 as v2

from source.geometry import angle_clamp
from source.globals  import *


class PlayerState:
    IDLE    = 0		# idle
    DELAY   = 1		# received orders, but we're waiting before we accept them (to emulate click delay)
    TURNING = 2		# turning
    MOVING  = 3		# moving


# player sprite size ~= 12x31
WALK_SPEED    = 3
PLAYER_RADIUS = 6


class Player:
    def __init__(self, pos, angle):
        self.pos   = pos
        self.angle = angle_clamp(angle)
        self.bbox  = (v2(self.pos.x - PLAYER_RADIUS, self.pos.y - PLAYER_RADIUS),
                      v2(self.pos.x + PLAYER_RADIUS, self.pos.y + PLAYER_RADIUS))
        self.state = PlayerState.IDLE

    def draw(self, screen, offset, draw_bounding_box=True):
        if draw_bounding_box:
            edges_to_draw = [(v2(self.bbox[0].x, self.bbox[0].y), v2(self.bbox[1].x, self.bbox[0].y)),
                             (v2(self.bbox[1].x, self.bbox[0].y), v2(self.bbox[1].x, self.bbox[1].y)),
                             (v2(self.bbox[1].x, self.bbox[1].y), v2(self.bbox[0].x, self.bbox[1].y)),
                             (v2(self.bbox[0].x, self.bbox[1].y), v2(self.bbox[0].x, self.bbox[0].y))]
            for edge in edges_to_draw:
                pg.draw.line(screen, Color.HITBOX, edge[0]+offset, edge[1]+offset, width=1)

    def update(self, player_inputs):
        dpos = v2(0,0)
        if player_inputs[PlayerInput.BUTTON_LEFT] and not player_inputs[PlayerInput.BUTTON_RIGHT]:
            dpos.x -= WALK_SPEED
        elif player_inputs[PlayerInput.BUTTON_RIGHT] and not player_inputs[PlayerInput.BUTTON_LEFT]:
            dpos.x += WALK_SPEED
        if player_inputs[PlayerInput.BUTTON_UP] and not player_inputs[PlayerInput.BUTTON_DOWN]:
            dpos.y -= WALK_SPEED
        elif player_inputs[PlayerInput.BUTTON_DOWN] and not player_inputs[PlayerInput.BUTTON_UP]:
            dpos.y += WALK_SPEED
        #
        self.update_position(self.pos + dpos, self.angle)

    def update_position(self, pos=None, angle=None):
        if pos is not None:
            self.pos  = pos
            self.bbox = (v2(self.pos.x - PLAYER_RADIUS, self.pos.y - PLAYER_RADIUS),
                         v2(self.pos.x + PLAYER_RADIUS, self.pos.y + PLAYER_RADIUS))
        if angle is not None:
            self.angle = angle
