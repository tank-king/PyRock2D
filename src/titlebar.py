"""
This class has been kept as reference
for now the functionality is not required in this app
"""

import ctypes

import pygame
from pygame._sdl2.video import Window

from src.globals import Globals, Config


class TitleBar:
    def __init__(self):
        self.window = Window.from_display_module()
        self._mouse_x, self._mouse_y = self.get_mouse_position()
        self._title_x, self._title_y = pygame.mouse.get_pos()
        self._title_selected = False

    @staticmethod
    def get_mouse_position():
        # function to get mouse coordinates in the entire window (single monitor)
        # partially based on this
        # https://stackoverflow.com/questions/3698635/how-to-get-the-text-cursor-position-in-windows
        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

        point = POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
        return point.x, point.y

    def title_bar(self, events, surf: pygame.Surface):
        rect = pygame.Rect(0, 0, Config.W, 40)
        pygame.draw.rect(surf, '#222222', rect)
        pos = pygame.mouse.get_pos()
        selected = False
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if rect.collidepoint(*pos):
                    selected = True
                    self._title_selected = True
                    self._title_x, self._title_y = pos
            if e.type == pygame.MOUSEBUTTONUP:
                self._title_selected = False
        mx, my = self.get_mouse_position()
        if self._title_selected:
            x = mx - self._title_x
            y = my - self._title_y
            if x < 0:
                x = 0
                if selected:
                    self._title_x = pos[0]
            elif x > Globals.SCREEN_WIDTH - Config.W:
                x = Globals.SCREEN_WIDTH - Config.W
                if selected:
                    self._title_x = pos[0]

            if y < 0:
                y = 0
                if selected:
                    self._title_y = pos[1]
            elif y > Globals.SCREEN_HEIGHT - rect.h:
                y = Globals.SCREEN_HEIGHT - rect.h
                if selected:
                    self._title_y = pos[1]

            self.window.position = [x, y]
        self._mouse_x, self._mouse_y = mx, my
