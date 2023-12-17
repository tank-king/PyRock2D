import ctypes
import sys
from pathlib import Path

import pygame

user32 = ctypes.windll.user32


# try:
#     user32 = ctypes.windll.user32
#     raise AttributeError
# except AttributeError:
#     # in a different OS
#     user32 = type(
#         'user32',
#         (),
#         {'GetSystemMetrics': lambda x: Config.W if x == 0 else Config.W}
#     )


class Config:
    W, H = 1200, 800
    FPS = 60
    TARGET_FPS = 60
    ASSETS = Path(__file__).parent.parent / 'assets'
    BACKUP_FONT_NAME = ASSETS / 'fonts' / 'font.ttf'
    FONT_NAME = 'consolas'
    FONT_SIZE = 30
    BG_COLOR = '#' + '11' * 3
    DEFAULT_DIALOG_BOX_SIZE = [500, 200]


class Globals:
    # Get the primary monitor
    SCREEN_WIDTH = user32.GetSystemMetrics(0)  # SM_CXSCREEN
    SCREEN_HEIGHT = user32.GetSystemMetrics(1)  # SM_CYSCREEN
    # SCREEN_WIDTH = 0
    # SCREEN_HEIGHT = 0
    min_padding = 100
    if SCREEN_WIDTH <= Config.W + min_padding:
        Config.W = SCREEN_WIDTH - min_padding
    if SCREEN_HEIGHT <= Config.H + min_padding:
        Config.H = SCREEN_HEIGHT - min_padding

    ROCK_WIDTH = Config.W * 0.6
    ROCK_HEIGHT = Config.H * 0.65
    ROCK_POINTS = 25
    ROCK_ANGLE = 0
    ROCK_COLOR = 'red'

    SLIDER_COORDS = [-1, [-1, -1]]

    LIGHT_COORD = [0, 0]
    LIGHTING_MOVE = False
    LIGHTING = True


class Events:
    (
        MOUSE_HOVERED,
        MOUSE_GRAB,
        *_
    ) = [pygame.event.custom_type() for _ in range(10)]


class BaseStructure:
    def update(self, events: list[pygame.event.Event], dt):
        pass

    def draw(self, screen: pygame.Surface):
        pass

    @staticmethod
    def post(event, **kwargs):
        pygame.event.post(pygame.event.Event(event, **kwargs))


def chain_function(f):
    # to be used only in methods
    self = None

    def inner(*args, **kwargs):
        nonlocal self
        f(*args, **kwargs)
        self = args[0]
        return self

    return inner


_font = None


def get_text(name, color='black', wraplength=0):
    global _font
    if not _font:
        if False and Config.FONT_NAME not in pygame.font.get_fonts():
            _font = pygame.font.Font(Config.BACKUP_FONT_NAME, Config.FONT_SIZE)
        else:
            _font = pygame.font.SysFont(Config.FONT_NAME, Config.FONT_SIZE)
    return _font.render(name, True, color, wraplength=wraplength)


# for closing pyinstaller splash screen if loaded from bundle

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    print('running in a PyInstaller bundle')
    BASE_PATH = sys._MEIPASS
    Config.ASSETS = Path(sys._MEIPASS, Config.ASSETS)
    Config.BACKUP_FONT_NAME = Config.ASSETS / 'fonts' / 'font.ttf'
    try:
        import pyi_splash

        pyi_splash.close()
    except ImportError:
        pass
else:
    print('running in a normal Python process')
