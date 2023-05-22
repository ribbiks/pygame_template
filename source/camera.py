from pygame.math import Vector2 as v2

from source.geometry import value_clamp
from source.globals  import *

MAX_CAMERA_SPEED = 16


class Camera:
    def __init__(self, pos):
        self.pos      = pos
        self.target   = None
        self.bounds   = None
        self.locked_x = False
        self.locked_y = False

    def set_target(self, pos):
        self.target = v2(RES)/2 - pos

    def set_bounds(self, xmin, xmax, ymin, ymax):
        sx = sorted([-xmin, RES[0] - xmax])
        sy = sorted([-ymin, RES[1] - ymax])
        self.bounds = (sx[0], sx[1], sy[0], sy[1])

    def update(self):
        if self.target is not None:
            d = self.target - self.pos
            if self.locked_x:
                d.x = 0.
            if self.locked_y:
                d.y = 0.
            dl = d.length()
            move_amt = dl*dl*0.008
            move_amt = value_clamp(move_amt, 0, MAX_CAMERA_SPEED)
            if move_amt > 0.04:
                d.scale_to_length(move_amt)
                self.pos += d
                self.pos = v2(value_clamp(self.pos.x, self.bounds[0], self.bounds[1]),
                              value_clamp(self.pos.y, self.bounds[2], self.bounds[3]))
