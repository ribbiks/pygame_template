import os
import pygame as pg

from pygame.math import Vector2 as v2

from source.geometry import angle_clamp
from source.globals  import *


class PlayerState:
    IDLE = 0		# idle
    WALK = 1		# walk
    SLASH_1 = 2
    SLASH_2 = 3
    SLASH_3 = 4


class CompassDir:
    E  = 0
    NE = 1
    N  = 2
    NW = 3
    W  = 4
    SW = 5
    S  = 6
    SE = 7


# (left, right, up, down)
MOVE_2_COMPASS = {(False,True,False,False):CompassDir.E, (False,True,True,False):CompassDir.NE,
                  (False,False,True,False):CompassDir.N, (True,False,True,False):CompassDir.NW,
                  (True,False,False,False):CompassDir.W, (True,False,False,True):CompassDir.SW,
                  (False,False,False,True):CompassDir.S, (False,True,False,True):CompassDir.SE}

COMPASS_VECS = [v2(1,0),  v2(1,-1)*ONE_OVER_ROOT2,
                v2(0,-1), v2(-1,-1)*ONE_OVER_ROOT2,
                v2(-1,0), v2(-1,1)*ONE_OVER_ROOT2,
                v2(0,1),  v2(1,1)*ONE_OVER_ROOT2]

# player sprite size ~= 12x31
WALK_SPEED    = 4
PLAYER_RADIUS = 5

SLASH_DURATION = 12
SLASH_BUFFER   = 6
SLASH_COOLDOWN_1 = SLASH_DURATION + 2
SLASH_COOLDOWN_2 = SLASH_DURATION + 4
SLASH_COOLDOWN_3 = SLASH_DURATION + 7

MOVE_DURING_SLASH = [0]*SLASH_DURATION
MOVE_DURING_SLASH[-3] = 2
MOVE_DURING_SLASH[-4] = 2
MOVE_DURING_SLASH[-5] = 1
MOVE_DURING_SLASH[-6] = 1
MOVE_DURING_SLASH[-7] = 1
MOVE_DURING_SLASH[-8] = 1

# game feel was designed around 30fps, some globals need to be modified for 60
HALVE_EVERYTHING = False
if FRAMERATE == 60:
    HALVE_EVERYTHING = True
#
if HALVE_EVERYTHING:
    WALK_SPEED       /= 2
    SLASH_DURATION   *= 2
    SLASH_BUFFER     *= 2
    SLASH_COOLDOWN_1 *= 2
    SLASH_COOLDOWN_2 *= 2
    SLASH_COOLDOWN_3 *= 2
    MOVE_DURING_SLASH = [[n/2, n/2] for n in MOVE_DURING_SLASH]
    MOVE_DURING_SLASH = [item for sublist in MOVE_DURING_SLASH for item in sublist]


class Player:
    def __init__(self, pos):
        self.pos   = pos
        self.bbox  = (v2(self.pos.x - PLAYER_RADIUS, self.pos.y - PLAYER_RADIUS),
                      v2(self.pos.x + PLAYER_RADIUS, self.pos.y + PLAYER_RADIUS))
        self.state = PlayerState.IDLE
        self.sprites = {}
        self.shadow_surface = None
        self.slash_timer = 0
        self.slash_cooldown = 0
        self.facing_dir = CompassDir.E

    def load_sprites(self, sprite_dir):
        self.sprites['shadow'] = (pg.image.load(os.path.join(sprite_dir, 'player_shadow.png')).convert_alpha(), v2(0,0))
        self.sprites['static'] = (pg.image.load(os.path.join(sprite_dir, 'player_placeholder.png')).convert_alpha(), v2(-6,-29))
        self.shadow_surface = pg.Surface(self.sprites['shadow'][0].get_size())
        self.shadow_surface.set_alpha(128)
        self.shadow_surface.blit(self.sprites['shadow'][0], (0,0))

    def draw(self, screen, offset, state_draw_font=None, draw_bounding_box=False):
        shadow_pos = self.shadow_surface.get_rect(center=self.shadow_surface.get_rect(center=self.pos + offset + self.sprites['shadow'][1]).center)
        screen.blit(self.shadow_surface, shadow_pos, special_flags=pg.BLEND_ALPHA_SDL2)
        #
        screen.blit(self.sprites['static'][0], self.pos + offset + self.sprites['static'][1])
        #
        if draw_bounding_box:
            edges_to_draw = [(v2(self.bbox[0].x, self.bbox[0].y), v2(self.bbox[1].x, self.bbox[0].y)),
                             (v2(self.bbox[1].x, self.bbox[0].y), v2(self.bbox[1].x, self.bbox[1].y)),
                             (v2(self.bbox[1].x, self.bbox[1].y), v2(self.bbox[0].x, self.bbox[1].y)),
                             (v2(self.bbox[0].x, self.bbox[1].y), v2(self.bbox[0].x, self.bbox[0].y))]
            for edge in edges_to_draw:
                pg.draw.line(screen, Color.HITBOX, edge[0]+offset, edge[1]+offset, width=1)
        #
        if state_draw_font:
            state_draw_font.render(screen, str(self.state), self.pos + offset, centered=False)

    def update(self, input_buffer):
        dpos = v2(0,0)
        player_inputs = input_buffer[-1]
        #
        move_left  = player_inputs[PlayerInput.BUTTON_LEFT] and not player_inputs[PlayerInput.BUTTON_RIGHT]
        move_right = player_inputs[PlayerInput.BUTTON_RIGHT] and not player_inputs[PlayerInput.BUTTON_LEFT]
        move_up    = player_inputs[PlayerInput.BUTTON_UP] and not player_inputs[PlayerInput.BUTTON_DOWN]
        move_down  = player_inputs[PlayerInput.BUTTON_DOWN] and not player_inputs[PlayerInput.BUTTON_UP]
        move_key   = (move_left, move_right, move_up, move_down)
        any_move   = any(move_key)
        if any_move:
            self.facing_dir = MOVE_2_COMPASS[move_key]
        #
        slash_inputs = []
        for i in range(len(input_buffer) - SLASH_BUFFER, len(input_buffer)):
            slash_inputs.append(input_buffer[i][PlayerInput.LEFT_CLICK_DN] or input_buffer[i][PlayerInput.BUTTON_X])
        any_slash = any(slash_inputs)
        #
        if self.slash_timer == 0:
            if self.state in [PlayerState.SLASH_1, PlayerState.SLASH_2, PlayerState.SLASH_3] or any_move is False:
                self.state = PlayerState.IDLE
        #
        if self.state in [PlayerState.IDLE, PlayerState.WALK] and self.slash_cooldown == 0:
            if any_slash:
                self.state = PlayerState.SLASH_1
                self.slash_timer = SLASH_DURATION
                self.slash_cooldown = SLASH_COOLDOWN_1
            elif any_move:
                self.state = PlayerState.WALK
                dpos += COMPASS_VECS[self.facing_dir]*WALK_SPEED
        elif self.state == PlayerState.SLASH_1 and any_slash and self.slash_timer == 1:
            self.state = PlayerState.SLASH_2
            self.slash_timer = SLASH_DURATION
            self.slash_cooldown = SLASH_COOLDOWN_2
        elif self.state == PlayerState.SLASH_2 and any_slash and self.slash_timer == 1:
            self.state = PlayerState.SLASH_3
            self.slash_timer = SLASH_DURATION
            self.slash_cooldown = SLASH_COOLDOWN_3
        #
        if self.slash_timer > 0:
            move_amt = MOVE_DURING_SLASH[self.slash_timer - 1]
            if self.facing_dir == CompassDir.E:
                dpos += v2(move_amt, 0)
            elif self.facing_dir == CompassDir.NE:
                dpos += v2(move_amt, -move_amt)*ONE_OVER_ROOT2
            elif self.facing_dir == CompassDir.N:
                dpos += v2(0, -move_amt)
            elif self.facing_dir == CompassDir.NW:
                dpos += v2(-move_amt, -move_amt)*ONE_OVER_ROOT2
            elif self.facing_dir == CompassDir.W:
                dpos += v2(-move_amt, 0)
            elif self.facing_dir == CompassDir.SW:
                dpos += v2(-move_amt, move_amt)*ONE_OVER_ROOT2
            elif self.facing_dir == CompassDir.S:
                dpos += v2(0, move_amt)
            elif self.facing_dir == CompassDir.SE:
                dpos += v2(move_amt, move_amt)*ONE_OVER_ROOT2
            self.slash_timer -= 1
        if self.slash_cooldown > 0:
            self.slash_cooldown -= 1
        #
        self.update_position(self.pos + dpos)

    def update_position(self, pos=None):
        if pos is not None:
            self.pos  = pos
            self.bbox = (v2(self.pos.x - PLAYER_RADIUS, self.pos.y - PLAYER_RADIUS),
                         v2(self.pos.x + PLAYER_RADIUS, self.pos.y + PLAYER_RADIUS))
