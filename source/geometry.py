from pygame.math import Vector2 as v2

from source.globals import SMALL_NUMBER


def angle_clamp(angle):
    if abs(angle) < SMALL_NUMBER:
        return 0.
    while angle < 0:
        angle += 360
    while angle > 360:
        angle -= 360
    return angle


def value_clamp(v, v_min, v_max):
    if v <= v_min:
        return v_min
    if v >= v_max:
        return v_max
    return v


def ranges_overlap(xmin1, xmax1, xmin2, xmax2):
    return (xmax1 >= xmin2 and xmax2 >= xmin1)


def ranges_overlap_excl(xmin1, xmax1, xmin2, xmax2):
    return (xmax1 > xmin2 and xmax2 > xmin1)


def boxes_overlap(b1, b2):
    return (ranges_overlap_excl(b1[0].x, b1[1].x, b2[0].x, b2[1].x) and
            ranges_overlap_excl(b1[0].y, b1[1].y, b2[0].y, b2[1].y))


def point_in_box(p, topleft, bottomright):
    return (p.x >= topleft.x and
            p.x <= bottomright.x and
            p.y >= topleft.y and
            p.y <= bottomright.y)


def point_in_box_excl(p, topleft, bottomright):
    return (p.x > topleft.x and
            p.x < bottomright.x and
            p.y > topleft.y and
            p.y < bottomright.y)
