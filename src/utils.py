import time
from typing import Literal, Union

import pygame
from pygame._sdl2 import Texture
from pygame.math import clamp


class Point(pygame.Vector2):
    pass


def map_value(value, from_min, from_max, to_min, to_max):
    clamped_value = max(min(value, from_max), from_min)
    mapped_value = (clamped_value - from_min) / (from_max - from_min) * (to_max - to_min) + to_min
    return mapped_value


def lerp(x, to_x, amt):
    return pygame.Vector2(x, x).lerp([to_x, to_x], amt).x


class Color(pygame.Color):
    def rgb(self):
        return self.r, self.g, self.b

    def rgba(self):
        return self.r, self.g, self.b, self.a

    def blend_colors(self, other: 'Color'):
        c = self * other + other * (1 - other.a / 255)

    def blend(self, other: 'Color'):
        return self * other
        # color = self * (self.a / 255) + other * (1 - other.a / 255)
        # color.a = self.a +

    # def blend_colors(self, other: 'Color', weight: float):
    #     r_result = max(0, min(int((1 - weight) * self.r + weight * other.r), 255))
    #     g_result = max(0, min(int((1 - weight) * self.g + weight * other.g), 255))
    #     b_result = max(0, min(int((1 - weight) * self.b + weight * other.b), 255))
    #
    #     return Color(r_result, g_result, b_result)

    def blend_mul(self, other: 'Color'):
        self.r = int(clamp(self.r * other.r / 255, 0, 255))
        self.g = int(clamp(self.g * other.g / 255, 0, 255))
        self.b = int(clamp(self.b * other.b / 255, 0, 255))
        self.a = int(clamp(self.a * other.a / 255, 0, 255))
        return self

    def __mul__(self, other: Union[int, float, 'Color']):
        if isinstance(other, int) or isinstance(other, float):
            self.r = int(clamp(self.r * other, 0, 255))
            self.g = int(clamp(self.g * other, 0, 255))
            self.b = int(clamp(self.b * other, 0, 255))
            return self
        else:
            return super().__mul__(other)


class SpriteSheet:
    """
    Class to load sprite-sheets
    """

    def __init__(self, renderer, sheet, rows, cols, images=None, alpha=True, scale=1.0, color_key=None):
        self._sheet = pygame.image.load(sheet)
        self.texture = Texture.from_surface(renderer, self._sheet)
        self._r = rows
        self._c = cols
        self._images = images if images else rows * cols
        self._alpha = alpha
        self.scale = scale
        self._color_key = color_key
        self.rects = self.get_rects()

    def __str__(self):
        return f'SpriteSheet Object <{self._sheet.__str__()}>'

    def get_rects(self):
        w = self._sheet.get_width() // self._c
        h = self._sheet.get_height() // self._r
        rects = [pygame.Rect(i % self._c * w, i // self._c * h, w, h) for i in
                 range(self._r * self._c)][0:self._images]
        return rects

    def get_images(self):
        w = self._sheet.get_width() // self._c
        h = self._sheet.get_height() // self._r
        images = [self._sheet.subsurface(pygame.Rect(i % self._c * w, i // self._c * h, w, h)) for i in
                  range(self._r * self._c)][0:self._images]
        if self._color_key is not None:
            for i in images:
                i.set_colorkey(self._color_key)
        if self._alpha:
            for i in images:
                i.convert_alpha()
        else:
            for i in images:
                i.convert()
        return [pygame.transform.scale_by(i, self.scale) for i in images]


class Timer:
    def __init__(self, timeout=0.0, reset=True, callback=None):
        self.timeout = timeout
        self.timer = time.time()
        self.paused_timer = time.time()
        self.paused = False
        self._reset = reset
        self.callback = callback

    def reset(self):
        self.timer = time.time()

    def pause(self):
        self.paused = True
        self.paused_timer = time.time()

    def resume(self):
        self.paused = False
        self.timer -= time.time() - self.paused_timer

    @property
    def elapsed(self):
        if self.paused:
            return time.time() - self.timer - (time.time() - self.paused_timer)
        return time.time() - self.timer

    @property
    def tick(self):
        if self.elapsed > self.timeout:
            if self._reset:
                self.timer = time.time()  # reset timer
            if self.callback:
                self.callback()
            return True
        else:
            return False


class LoopingSpriteSheet:
    def __init__(self, renderer, sheet, rows, cols, images=None, alpha=True, scale=1.0, color_key=None, timer=0.1,
                 mode: Literal['center', 'topleft'] = 'center'):
        self.timer = Timer(timeout=timer)
        self.sheet = SpriteSheet(renderer, sheet, rows, cols, images, alpha, scale, color_key)
        self.c = 0
        self.mode = mode

    def draw(self, x, y, angle=0, flip_x=False, flip_y=False):
        if self.timer.tick:
            self.c += 1
            self.c %= len(self.sheet.rects)
        rect = self.sheet.rects[self.c]
        k = self.sheet.scale
        if self.mode == 'center':
            self.sheet.texture.draw(rect, pygame.Rect(x - rect.w * k / 2, y - rect.h * k / 2, rect.w * k, rect.h * k),
                                    angle, flip_x=flip_x, flip_y=flip_y)
            # renderer.blit(
            #     self.sheet.texture,
            #     dest=pygame.Rect(x - rect.w * k / 2, y - rect.h * k / 2, rect.w * k, rect.h * k),
            #     area=rect
            # )
        else:
            self.sheet.texture.draw(rect, pygame.Rect(x, y, rect.w * k, rect.h * k), angle, flip_x=flip_x,
                                    flip_y=flip_y)
            # renderer.blit(
            #     self.sheet.texture,
            #     dest=pygame.Rect(x, y, rect.w * k, rect.h * k),
            #     area=rect
            # )
