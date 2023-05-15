import argparse
import pygame as pg
import sys

from source.globals import *

#
class InputManager:
	#
	#
	#
	def __init__(self):
		self.joysticks = {}

	#
	#
	#
	def get_inputs_from_events(self, pg_events):
		#
		all_inputs = [False]*NUM_INPUTS
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
			#
			elif event.type == pg.MOUSEBUTTONDOWN:
				if event.button == 1:
					all_inputs[PlayerInput.LEFT_CLICK_DN] = True
				if event.button == 3:
					all_inputs[PlayerInput.RIGHT_CLICK_DN] = True
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
		for joystick in self.joysticks.values():
			#
			axes = joystick.get_numaxes()
			if axes != len(JOYSTICK_AXIS_TO_BUTTON):
				print('What kind of controller are you? # axes =', axes)
				exit(1)
			for i in range(axes):
				axis = joystick.get_axis(i)
				if abs(axis) >= JOYSTICK_AXIS_THRESH:
					if axis < 0 and JOYSTICK_AXIS_TO_BUTTON[i][0] != None:
						all_inputs[JOYSTICK_AXIS_TO_BUTTON[i][0]] = True
					if axis > 0 and JOYSTICK_AXIS_TO_BUTTON[i][1] != None:
						all_inputs[JOYSTICK_AXIS_TO_BUTTON[i][1]] = True
			#
			numhats = joystick.get_numhats()
			if numhats >= 1:
				hat = joystick.get_hat(0)
				if hat[0] == -1:
					all_inputs[PlayerInput.BUTTON_LEFT] = True
				elif hat[0] == 1:
					all_inputs[PlayerInput.BUTTON_RIGHT] = True
				if hat[1] == -1:
					all_inputs[PlayerInput.BUTTON_DOWN] = True
				elif hat[1] == 1:
					all_inputs[PlayerInput.BUTTON_UP] = True
			#
			buttons = joystick.get_numbuttons()
			if buttons != len(JOYSTICK_BUTTON_TO_INPUT):
				print('What kind of controller are you? # buttons =', buttons)
				exit(1)
			for i in range(buttons):
				button = joystick.get_button(i)
				if button == 1 and JOYSTICK_BUTTON_TO_INPUT[i] != None:
					all_inputs[JOYSTICK_BUTTON_TO_INPUT[i]] = True
		#
		return all_inputs

#
#
#
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

#
# axis 0: left-stick X
# axis 1: left-stick Y
# axis 2: L2            (positive only)
# axis 3: right-stick X
# axis 4: right-stick Y
# axis 5: R2            (positive only)
#
JOYSTICK_AXIS_TO_BUTTON = [(PlayerInput.BUTTON_LEFT, PlayerInput.BUTTON_RIGHT),
                           (PlayerInput.BUTTON_UP,   PlayerInput.BUTTON_DOWN),
                           (None, PlayerInput.BUTTON_L2),
                           (None, None),
                           (None, None),
                           (None, PlayerInput.BUTTON_R2)]

JOYSTICK_AXIS_THRESH = 0.500

JOYSTICK_BUTTON_TO_INPUT = [PlayerInput.BUTTON_A,
                            PlayerInput.BUTTON_B,
                            PlayerInput.BUTTON_X,
                            PlayerInput.BUTTON_Y,
                            PlayerInput.BUTTON_L1,
                            PlayerInput.BUTTON_R1,
                            None,
                            None,
                            PlayerInput.SELECT,
                            PlayerInput.START]
