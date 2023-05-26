import argparse
import pygame as pg
import sys

from source.globals import *


class InputManager:
    #
    #
    #
    def __init__(self):
        self.held_inputs = [False]*NUM_INPUTS
        self.prev_inputs = [False]*NUM_INPUTS
        self.joysticks = {}
        self.recent_input_was_joystick = False

    #
    #
    #
    def get_inputs_from_events(self, pg_events):
        #
        all_inputs = [False]*NUM_INPUTS
        #
        # get M + K inputs
        #
        for event in pg_events:
            #
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            #
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    all_inputs[PlayerInput.ESCAPE] = True
                    all_inputs[PlayerInput.START] = True
                if event.key == pg.K_TAB:
                    all_inputs[PlayerInput.SELECT] = True
                if event.key == pg.K_w or event.key == pg.K_UP:
                    all_inputs[PlayerInput.BUTTON_UP] = True
                    self.held_inputs[PlayerInput.BUTTON_UP] = True
                if event.key == pg.K_a or event.key == pg.K_LEFT:
                    all_inputs[PlayerInput.BUTTON_LEFT] = True
                    self.held_inputs[PlayerInput.BUTTON_LEFT] = True
                if event.key == pg.K_s or event.key == pg.K_DOWN:
                    all_inputs[PlayerInput.BUTTON_DOWN] = True
                    self.held_inputs[PlayerInput.BUTTON_DOWN] = True
                if event.key == pg.K_d or event.key == pg.K_RIGHT:
                    all_inputs[PlayerInput.BUTTON_RIGHT] = True
                    self.held_inputs[PlayerInput.BUTTON_RIGHT] = True
                if event.key == pg.K_SPACE:
                    all_inputs[PlayerInput.BUTTON_A] = True
                if event.key == pg.K_q:
                    all_inputs[PlayerInput.BUTTON_B] = True
                if event.key == pg.K_e:
                    all_inputs[PlayerInput.BUTTON_Y] = True
            #
            elif event.type == pg.KEYUP:
                if event.key == pg.K_w or event.key == pg.K_UP:
                    self.held_inputs[PlayerInput.BUTTON_UP] = False
                if event.key == pg.K_a or event.key == pg.K_LEFT:
                    self.held_inputs[PlayerInput.BUTTON_LEFT] = False
                if event.key == pg.K_s or event.key == pg.K_DOWN:
                    self.held_inputs[PlayerInput.BUTTON_DOWN] = False
                if event.key == pg.K_d or event.key == pg.K_RIGHT:
                    self.held_inputs[PlayerInput.BUTTON_RIGHT] = False
            #
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    all_inputs[PlayerInput.LEFT_CLICK_DN] = True
                    all_inputs[PlayerInput.BUTTON_X] = True
                if event.button == 3:
                    all_inputs[PlayerInput.RIGHT_CLICK_DN] = True
                    all_inputs[PlayerInput.BUTTON_R2] = True
            #
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    all_inputs[PlayerInput.LEFT_CLICK_UP] = True
                if event.button == 3:
                    all_inputs[PlayerInput.RIGHT_CLICK_UP] = True
            #
            elif event.type == pg.JOYDEVICEADDED:
                joy = pg.joystick.Joystick(event.device_index)
                self.joysticks[joy.get_instance_id()] = joy
                print(f"Joystick {joy.get_instance_id()} connected")
            #
            elif event.type == pg.JOYDEVICEREMOVED:
                del self.joysticks[event.instance_id]
                print(f"Joystick {event.instance_id} disconnected")
        #
        all_inputs = [n | self.held_inputs[i] for i,n in enumerate(all_inputs)]
        #
        if any(all_inputs):
            self.recent_input_was_joystick = False
        #
        # get joystick inputs
        #
        for joystick in self.joysticks.values():
            #
            num_axes    = joystick.get_numaxes()
            num_hats    = joystick.get_numhats()
            num_buttons = joystick.get_numbuttons()
            (joy_axis_layout, joy_button_layout) = get_joystick_layout(num_axes, num_buttons, num_hats)
            #
            for i in range(len(joy_axis_layout)):
                axis = joystick.get_axis(i)
                if abs(axis) >= JOYSTICK_AXIS_THRESH:
                    if axis < 0 and joy_axis_layout[i][0] is not None:
                        all_inputs[joy_axis_layout[i][0]] = True
                        self.recent_input_was_joystick = True
                    if axis > 0 and joy_axis_layout[i][1] is not None:
                        all_inputs[joy_axis_layout[i][1]] = True
                        self.recent_input_was_joystick = True
            #
            for i in range(len(joy_button_layout)):
                button = joystick.get_button(i)
                if button == 1 and joy_button_layout[i] is not None:
                    all_inputs[joy_button_layout[i]] = True
                    self.recent_input_was_joystick = True
            #
            if num_hats >= 1:
                hat = joystick.get_hat(0)
                if hat[0] == -1:
                    all_inputs[PlayerInput.BUTTON_LEFT] = True
                    self.recent_input_was_joystick = True
                elif hat[0] == 1:
                    all_inputs[PlayerInput.BUTTON_RIGHT] = True
                    self.recent_input_was_joystick = True
                if hat[1] == -1:
                    all_inputs[PlayerInput.BUTTON_DOWN] = True
                    self.recent_input_was_joystick = True
                elif hat[1] == 1:
                    all_inputs[PlayerInput.BUTTON_UP] = True
                    self.recent_input_was_joystick = True
        #
        input_mask = [True]*NUM_INPUTS
        for k in JOY_BUTTON_REQUIRES_LIFT_BEFORE_REFIRE:
            if self.prev_inputs[k]:
                input_mask[k] = False
        self.prev_inputs = [n for n in all_inputs]
        all_inputs = [n & input_mask[i] for i,n in enumerate(all_inputs)]
        #
        return all_inputs


def get_input_args():
    parser = argparse.ArgumentParser(description=GAME_VERS, formatter_class=argparse.ArgumentDefaultsHelpFormatter,)
    parser.add_argument('-display', type=int, required=False, metavar='0',         help="which display to use [0 = primary]", default=0)
    parser.add_argument('-scale',   type=int, required=False, metavar='0',         help="scale factor [0 = automatic]",       default=0)
    parser.add_argument('--fullscreen',       required=False, action='store_true', help="run in fullscreen",                  default=False)
    args = parser.parse_args()
    #
    DISPLAY_NUM    = args.display
    SCALE_FACTOR   = args.scale
    RUN_FULLSCREEN = args.fullscreen
    #
    return [DISPLAY_NUM, SCALE_FACTOR, RUN_FULLSCREEN]


def get_joystick_layout(num_axes, num_buttons, num_hats):
    #
    # CONFIGURATION 1: [6 axes, 10 buttons, 1 hat] generic gamepad + desktop + MacOS13
    #
    # axis 0: left-stick X
    # axis 1: left-stick Y
    # axis 2: L2            (positive only)
    # axis 3: right-stick X
    # axis 4: right-stick Y
    # axis 5: R2            (positive only)
    #
    # button 0: A
    # button 1: B
    # button 2: X
    # button 3: Y
    # button 4: L1
    # button 5: R1
    # button 6: left-stick-press
    # button 7: right-stick-press
    # button 8: select
    # button 9: start
    #
    if (num_axes, num_buttons, num_hats) == (6, 10, 1):
        joy_axis_layout = [(PlayerInput.BUTTON_LEFT, PlayerInput.BUTTON_RIGHT),
                           (PlayerInput.BUTTON_UP,   PlayerInput.BUTTON_DOWN),
                           (None, PlayerInput.BUTTON_L2),
                           (None, None),
                           (None, None),
                           (None, PlayerInput.BUTTON_R2)]
        joy_button_layout = [PlayerInput.BUTTON_A,
                             PlayerInput.BUTTON_B,
                             PlayerInput.BUTTON_X,
                             PlayerInput.BUTTON_Y,
                             PlayerInput.BUTTON_L1,
                             PlayerInput.BUTTON_R1,
                             None,
                             None,
                             PlayerInput.SELECT,
                             PlayerInput.START]
    #
    # CONFIGURATION 2: [4 axes, 12 buttons, 1 hat] generic gamepad + desktop + Windows10
    #
    # axis 0: left-stick X
    # axis 1: left-stick Y
    # axis 2: right-stick X
    # axis 3: right-stick Y
    #
    # button 0: X
    # button 1: A
    # button 2: B
    # button 3: Y
    # button 4: L1
    # button 5: R1
    # button 6: L2
    # button 7: R2
    # button 8: select
    # button 9: start
    # button 10: left-stick-press
    # button 11: right-stick-press
    #
    elif (num_axes, num_buttons, num_hats) == (4, 12, 1):
        joy_axis_layout = [(PlayerInput.BUTTON_LEFT, PlayerInput.BUTTON_RIGHT),
                           (PlayerInput.BUTTON_UP,   PlayerInput.BUTTON_DOWN),
                           (None, None),
                           (None, None)]
        joy_button_layout = [PlayerInput.BUTTON_X,
                             PlayerInput.BUTTON_A,
                             PlayerInput.BUTTON_B,
                             PlayerInput.BUTTON_Y,
                             PlayerInput.BUTTON_L1,
                             PlayerInput.BUTTON_R1,
                             PlayerInput.BUTTON_L2,
                             PlayerInput.BUTTON_R2,
                             PlayerInput.SELECT,
                             PlayerInput.START,
                             None,
                             None]
    #
    # CONFIGURATION 3: [4 axes, 16 buttons, 0 hat] generic gamepad + web + Windows10
    #
    # axis 0: left-stick X
    # axis 1: left-stick Y
    # axis 2: right-stick X
    # axis 3: right-stick Y
    #
    # button 0: A
    # button 1: B
    # button 2: X
    # button 3: Y
    # button 4: L1
    # button 5: R1
    # button 6: L2
    # button 7: R2
    # button 8: select
    # button 9: start
    # button 10: left-stick-press
    # button 11: right-stick-press
    # button 12: up
    # button 13: down
    # button 14: left
    # button 15: right
    #
    elif (num_axes, num_buttons, num_hats) == (4, 16, 0):
        joy_axis_layout = [(PlayerInput.BUTTON_LEFT, PlayerInput.BUTTON_RIGHT),
                           (PlayerInput.BUTTON_UP,   PlayerInput.BUTTON_DOWN),
                           (None, None),
                           (None, None)]
        joy_button_layout = [PlayerInput.BUTTON_A,
                             PlayerInput.BUTTON_B,
                             PlayerInput.BUTTON_X,
                             PlayerInput.BUTTON_Y,
                             PlayerInput.BUTTON_L1,
                             PlayerInput.BUTTON_R1,
                             PlayerInput.BUTTON_L2,
                             PlayerInput.BUTTON_R2,
                             PlayerInput.SELECT,
                             PlayerInput.START,
                             None,
                             None,
                             PlayerInput.BUTTON_UP,
                             PlayerInput.BUTTON_DOWN,
                             PlayerInput.BUTTON_LEFT,
                             PlayerInput.BUTTON_RIGHT]
    else:
        print('Unknown controller type!', (num_axes, num_buttons, num_hats))
        joy_axis_layout   = []
        joy_button_layout = []
    return (joy_axis_layout, joy_button_layout)


JOYSTICK_AXIS_THRESH = 0.500

JOY_BUTTON_REQUIRES_LIFT_BEFORE_REFIRE = [PlayerInput.BUTTON_A,
                                          PlayerInput.BUTTON_B,
                                          PlayerInput.BUTTON_X,
                                          PlayerInput.BUTTON_Y,
                                          PlayerInput.BUTTON_L1,
                                          PlayerInput.BUTTON_L2,
                                          PlayerInput.BUTTON_R1,
                                          PlayerInput.BUTTON_R2,
                                          PlayerInput.SELECT,
                                          PlayerInput.START]
