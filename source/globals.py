import platform

GAME_VERS = 'Blah v0.0'
FRAMERATE = 30
RES       = (480,270)
GRID_SIZE = 16

# are we making the web version?
PYGBAG = False
if platform.system().lower() == "emscripten":
    # Note that this stuff only resolves when running in a web context
    PYGBAG = __WASM__ and __EMSCRIPTEN__ and __EMSCRIPTEN__.is_browser

# opacity (out of 255) for fading to black during screen transitions
# -- gamestate changes occur on the first instance of 255
FADE_SEQUENCE = [25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 255, 250, 225, 200, 175, 150, 125, 100, 50]

# max number of frames to allow to be updated once per draw
MAX_UPDATE_FRAMES = 8

# number of consecutive frames to use for estimating fps
NUM_FRAMES_FOR_FPS = MAX_UPDATE_FRAMES + 30

# basically a tolerance for floating point precision when determining equalities
SMALL_NUMBER = 1e-3

# used for various geometry
ONE_OVER_ROOT2 = 0.707106781186

MOUSE_TARGET_WEIGHT = 0.15


class PlayerInput:
    ESCAPE         = 0
    LEFT_CLICK_DN  = 1
    LEFT_CLICK_UP  = 2
    RIGHT_CLICK_DN = 3
    RIGHT_CLICK_UP = 4
    BUTTON_LEFT    = 5
    BUTTON_RIGHT   = 6
    BUTTON_DOWN    = 7
    BUTTON_UP      = 8
    BUTTON_A       = 9
    BUTTON_B       = 10
    BUTTON_X       = 11
    BUTTON_Y       = 12
    BUTTON_L1      = 13
    BUTTON_L2      = 14
    BUTTON_R1      = 15
    BUTTON_R2      = 16
    SELECT         = 17
    START          = 18


NUM_INPUTS = len([n for n in dir(PlayerInput) if n[:2] != '__'])
INPUT_BUFF_SIZE = 32


class Color:
    BLACK       = (  0,  0,  0)
    WHITE       = (255,255,255)
    GRID_MAJOR  = ( 36, 36, 36)
    GRID_MINOR  = ( 22, 22, 22)
    HITBOX      = (200, 200, 100)   # player debug hitbox


class GameStateNum:
    MAIN_MENU = 0
    SAVE_MENU = 1
    GAME      = 2
    PAUSE     = 3
