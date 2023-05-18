import pygame as pg

from pygame.math import Vector2 as v2

from source.globals import *


def draw_grid(screen, screensize, gridsize, offset, color):
    for x in range(0, int(screensize[0])+2, gridsize):
        p1 = v2(x, -gridsize)
        p2 = v2(x, screensize[1] + gridsize)
        pg.draw.line(screen, color, p1+offset, p2+offset, width=1)
    for y in range(0, int(screensize[1])+2, gridsize):
        p1 = v2(-gridsize, y)
        p2 = v2(screensize[0] + gridsize, y)
        pg.draw.line(screen, color, p1+offset, p2+offset, width=1)


def draw_fullscreen_border(screen, offset, screensize):
    fso_box_p1 = v2(offset) + v2(-1, -1)
    fso_box_p2 = v2(offset) + v2(screensize[0], -1)
    fso_box_p3 = v2(offset) + v2(screensize)
    fso_box_p4 = v2(offset) + v2(-1, screensize[1])
    pg.draw.line(screen, Color.WHITE, fso_box_p1, fso_box_p2, width=1)
    pg.draw.line(screen, Color.WHITE, fso_box_p2, fso_box_p3, width=1)
    pg.draw.line(screen, Color.WHITE, fso_box_p3, fso_box_p4, width=1)
    pg.draw.line(screen, Color.WHITE, fso_box_p4, fso_box_p1, width=1)
