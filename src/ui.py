import math
from functools import lru_cache

import pygame
from pygame.math import clamp

from src.globals import BaseStructure, Config, Events, get_text
from src.utils import Timer, Point


class UI(BaseStructure):
    def __init__(self, rect):
        self.rect = pygame.Rect(*rect)

    @property
    def x(self):
        return self.rect.x

    @x.setter
    def x(self, value):
        self.x += value

    @property
    def y(self):
        return self.rect.x

    @y.setter
    def y(self, value):
        self.x += value

    @property
    def pos(self):
        return self.x, self.y

    @pos.setter
    def pos(self, value):
        self.x, self.y = value


class Button(UI):
    def __init__(self, name, action=None, repeat=False, **kwargs):
        # self.text = self.text.subsurface(self.text.get_bounding_rect())
        self.name = name
        super().__init__(self.text.get_rect().scale_by(1.4, 1))
        for i in kwargs:
            try:
                self.rect.__setattr__(i, kwargs[i])
            except AttributeError:
                pass
        self.repeat = repeat
        self.action = action
        self.hovered = False
        self._re_adjust = False
        self._old_screen_dimensions = pygame.display.get_window_size()
        self._cap_x = 0, Config.W
        self._cap_y = 0, Config.H
        self.selected = False
        self.click_timer = Timer(0.01)
        self.click_delay_timer = Timer(0.5)
        self.click_repeat = False

    @property
    def text(self):
        return get_text(self.name, 'black')

    def readjust(self):
        self._re_adjust = True
        return self

    def cap_x(self, start, end):
        self._cap_x = start, end

    def cap_y(self, start, end):
        self._cap_y = start, end

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        if self._cap_x[0] != -1:
            self.rect.x = pygame.math.clamp(self.rect.x, *self._cap_x)
        if self._cap_y[0] != -1:
            self.rect.y = pygame.math.clamp(self.rect.y, *self._cap_y)

    def update(self, events: list[pygame.event.Event], dt):
        if self._re_adjust and self._old_screen_dimensions != (c := pygame.display.get_window_size()):
            w1, h1 = c
            w2, h2 = self._old_screen_dimensions
            dw, dh = w2 - w1, h2 - h1
            self.move(-dw, -dh)
            self._old_screen_dimensions = c
        mx, my = pygame.mouse.get_pos()
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    if self.rect.collidepoint(mx, my):
                        if self.repeat:
                            self.click_delay_timer.reset()
                            if self.action:
                                self.action()
                        self.selected = True
            if e.type == pygame.MOUSEBUTTONUP:
                if self.rect.collidepoint(mx, my) and not self.repeat:
                    if self.action:
                        self.action()
                self.selected = False
                self.click_repeat = False
                self.click_delay_timer.reset()
                self.click_timer.reset()
        if self.rect.collidepoint(mx, my):
            self.hovered = True
            self.post(Events.MOUSE_HOVERED)
        else:
            self.hovered = False

        if self.selected and self.repeat:
            if self.click_delay_timer.tick:
                self.click_repeat = True
            if self.click_repeat:
                if self.click_timer.tick:
                    if self.action:
                        self.action()

    def draw(self, screen: pygame.Surface):
        color = 'orange' if self.hovered else 'white'
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        if self.selected:
            t = pygame.transform.smoothscale_by(self.text, 0.9)
            # pygame.draw.rect(screen, 'brown', self.rect, 5, border_radius=5)
        else:
            t = self.text
        screen.blit(t, t.get_rect(center=self.rect.center))


class SpinBoxNumeric(UI):
    def __init__(self, low=0, high=100, initial=None, action=None):
        self.max_digits = len(max(str(low), str(high), key=len))
        self.low = low
        self.high = high
        self.action = action
        self.value = 0 if not initial else initial
        t = get_text('@' * self.max_digits, 'white')
        self.decrease = decrease = Button('<', self.decrease_value, True)
        self.increase = increase = Button('>', self.increase_value, True)
        super().__init__([0, 0, t.get_width() + decrease.rect.w + increase.rect.w, t.get_height()])
        # self.update_text()

    @property
    def text(self):
        return get_text(self.get_text(), 'white')

    def increase_value(self):
        if self.high != '...' and self.value >= self.high:
            return
        self.value += 1
        if self.action:
            self.action()
        # self.update_text()

    def decrease_value(self):
        if self.low != '...' and self.value <= self.low:
            return
        self.value -= 1
        if self.action:
            self.action()
        # self.update_text()

    def get_text(self):
        return ' ' + (s := str(self.value)) + ' ' * (self.max_digits - len(s) - 1)

    # def update_text(self):
    #     self.text = pygame.font.SysFont(Config.FONT_NAME, Config.FONT_SIZE).render(self.get_text(), True, 'white')

    def update(self, events: list[pygame.event.Event], dt):
        self.decrease.rect.topleft = [self.rect.x + self.text.get_width(), self.rect.y]
        self.increase.rect.topleft = self.decrease.rect.topright
        self.increase.update(events, dt)
        self.decrease.update(events, dt)

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, 'white', self.rect, 4, border_radius=10)
        screen.blit(self.text, self.text.get_rect(midleft=[self.rect.x, self.rect.y + self.rect.h // 2 + 2]))
        self.increase.draw(screen)
        self.decrease.draw(screen)


class TextBox(UI):
    def __init__(self, max_chars=20, initial='enter text'):
        t = get_text('@' * (max_chars + 2))
        super().__init__(t.get_rect())
        self.max_chars = max_chars
        self.initial = initial
        self.blink_timer = Timer(0.5)
        self.cursor_visible = False
        self.value = ''
        self.selected = False

    def update(self, events: list[pygame.event.Event], dt):
        mx, my = pygame.mouse.get_pos()
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self.rect.collidepoint(mx, my):
                    self.selected = True
                else:
                    self.selected = False
            if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                if not self.rect.collidepoint(mx, my):
                    self.selected = False
            if self.selected:
                if e.type == pygame.TEXTINPUT:
                    if len(self.value) < self.max_chars:
                        self.value += e.text
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_BACKSPACE:
                        if self.value:
                            self.value = self.value[:-1]

    def draw(self, screen: pygame.Surface):
        text = self.value if self.value else self.initial
        if self.selected:
            text = self.value
            if self.blink_timer.tick:
                self.cursor_visible = not self.cursor_visible
            if self.cursor_visible:
                text += '_'
            else:
                text += ' '
        t = get_text(text, color='white')
        pygame.draw.rect(screen, 'white' if not self.selected else 'orange', self.rect, 2, border_radius=10)
        screen.blit(t, t.get_rect(center=self.rect.center))


class Slider(UI):
    def __init__(self, width, height, img=None,
                 initial_value=0, outline=2, y_axis=False,
                 action=None):
        super().__init__([0, 0, width, height])
        self.action = action
        self.outline = outline
        if img:
            self.img = img
        else:
            self.img = pygame.Surface([width, height])
            self.img.fill(Config.BG_COLOR)
            # pygame.draw.rect(self.img, 'white', self.rect, 2, border_radius=10)
        self.selected = False
        self.y_axis = y_axis
        self._coord = [initial_value, 0] if type(initial_value) in [int, float] else initial_value
        self.value = self.get_value(*self.coord)

    @property
    def coord(self):
        if self.y_axis:
            return self._coord
        else:
            return [self._coord[0], self.rect.h / 2]

    @coord.setter
    def coord(self, value):
        self._coord = [clamp(value[0], 0, self.rect.w - 1), clamp(value[1], 0, self.rect.h - 1)]

    def get_value(self, x, y, color=False):
        self.coord = x, y
        if self.y_axis or color:
            return self.img.get_at(self.coord)
        else:
            return pygame.math.clamp(x, 0, self.rect.w - 1)

    @property
    def selection_height(self):
        if self.y_axis:
            return 20
        else:
            return max(20, self.rect.height)

    @property
    def selectable_rect(self):
        selectable_rect = pygame.Rect(0, 0, self.selection_height, self.selection_height)
        selectable_rect.center = [self.rect.x + self.coord[0], self.rect.y + self.coord[1]]
        return selectable_rect

    def update_value(self):
        self.value = self.get_value(*self.coord)

    def update(self, events: list[pygame.event.Event], dt):
        mx, my = pygame.mouse.get_pos()
        hovered = False
        if self.selectable_rect.collidepoint(mx, my):
            self.post(Events.MOUSE_HOVERED)
            hovered = True
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if hovered:
                    self.selected = True
            if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                self.selected = False

        if self.selected:
            self.value = self.get_value(mx - self.rect.x, my - self.rect.y)
        # self.value = pygame.math.clamp(self.value, 0, self.rect.w - 1)
        if self.selected:
            if self.action:
                self.action()

    def draw(self, screen: pygame.Surface):
        screen.blit(self.img, self.rect)
        rect = self.selectable_rect
        if self.outline:
            pygame.draw.rect(screen, 'white', self.rect, self.outline)
        self.img.lock()
        try:
            color = self.img.get_at(self.coord)
        except IndexError:
            color = self.img.get_at([0, 0])
        pygame.draw.circle(screen, color, [*rect.center], self.selection_height / 2)
        self.img.unlock()
        pygame.draw.circle(screen, 'white', [*rect.center], self.selection_height / 2, 2)


class ColorPicker(UI):
    def __init__(self, width, height, initial_values=None):
        assert height >= 50, width >= 200
        self.slider_height = 5
        v1, v2 = initial_values
        if v1 == -1:
            v1 = 0
        if v2 == [-1, -1]:
            v2 = width * 0.8 - 1
        # self.gradient = self.get_gradient(width * 0.8, height - 20)
        self.gradient_slider = Slider(width * 0.8, height - self.slider_height - 15,
                                      self.get_gradient(width * 0.8, height - self.slider_height - 15), outline=0,
                                      y_axis=True, initial_value=v2, action=self.gradient_slider_action)
        self.output_box = pygame.Surface([width * 0.2, self.gradient_slider.rect.h])
        self.slider = Slider(width, self.slider_height, img := self.slider_image(width, self.slider_height),
                             initial_value=v1, outline=0, action=self.slider_action)
        self.slider_img = img

        super().__init__([0, 0, width, height])
        self.update_timer = Timer(0.1)
        self.slider_action(force=True)
        self.gradient_slider_action()

        # function call for caching (requires approx 25 - 20 MB RAM)
        # self.slider_img.lock()
        # img = self.slider_img
        # _, h = self.slider_img.get_size()
        # for i in range(self.slider_img.get_width()):
        #     c = img.get_at([i, h // 2])
        #     print(i, _)
        #     self.get_gradient(width * 0.8, height - self.slider_height - 15, hex(c))
        # self.slider_img.unlock()

    def set_val(self, val):
        self.output_box.fill(val)
        # self.slider.

    @property
    def slider_coords(self):
        return [self.slider.value, self.gradient_slider.coord]

    @property
    def value(self):
        return self.output_box.get_at([0, 0])

    def slider_action(self, force=False):
        if self.update_timer.tick or force:
            width, height = self.rect.size
            color = self.slider.img.get_at(self.slider.coord)
            self.gradient_slider.img = self.get_gradient(width * 0.8, height - self.slider_height - 15, hex(color))
            self.gradient_slider.update_value()
            self.gradient_slider_action()

    def gradient_slider_action(self):
        color = self.gradient_slider.value
        self.output_box.fill(color)

    def update(self, events: list[pygame.event.Event], dt):
        for i in (self.slider, self.gradient_slider,):
            i.update(events, dt)

    def draw(self, screen: pygame.Surface):
        rect = self.output_box.get_rect()
        rect.topleft = self.rect.topleft
        screen.blit(self.output_box, rect)
        rect.topleft = rect.topright
        self.gradient_slider.rect.topleft = rect.topleft
        self.gradient_slider.draw(screen)
        self.slider.rect.topleft = Point(*self.rect.bottomleft) + [0, -self.slider_height]
        self.slider.draw(screen)
        # screen.blit(self.gradient, rect)

    @staticmethod
    @lru_cache(maxsize=400)
    def get_gradient(w, h, _color='red'):
        _color = [*pygame.Color(_color)]

        # def fragment(x, y, base_color):
        #     r1, g1, b1, a1 = [i / 255 for i in base_color]
        #     r = g = b = (1 - y ** 0.5)
        #     a = x * (1 - y)
        #
        #     final_color = (
        #         r * (1 - a) + r1 * a,
        #         g * (1 - a) + g1 * a,
        #         b * (1 - a) + b1 * a,
        #         1
        #     )
        #
        #     return [round(255 * clamp(i, 0, 1)) for i in final_color]
        # def fragment(x, y, base_color):
        #     r1, g1, b1, a1 = [i / 255 for i in base_color]
        #
        #     r = g = b = (1 - sqrt(y))
        #     a = x * (1 - y)
        #     one_minus_a = 1 - a
        #     final_color = (
        #         int(255 * (r * one_minus_a + r1 * a)),
        #         int(255 * (g * one_minus_a + g1 * a)),
        #         int(255 * (b * one_minus_a + b1 * a)),
        #         255  # Assuming alpha values are in the range [0, 255]
        #     )
        #
        #     return final_color

        sqrt = math.sqrt

        def fragment(x, y, base_color):
            r1, g1, b1, a1 = base_color
            r = g = b = 255 * (1 - sqrt(y))
            a = x * (1 - y)
            one_minus_a = 1 - a
            final_color = (
                r * one_minus_a + r1 * a,
                g * one_minus_a + g1 * a,
                b * one_minus_a + b1 * a,
                255
            )

            return final_color

        def shader(width, height, base_color):
            width = int(width)
            height = int(height)
            surf = pygame.Surface([width, height])
            # surf.fill(base_color)

            surf.lock()
            # t = time.time()
            # fragment = lambda x, y, z: (255, 0, 0, 255)
            for x in range(width):
                for y in range(height):
                    color = fragment(x / width, y / height, base_color)
                    surf.set_at([x, y], [*color])
            # one liner for performance
            # [surf.set_at([x, y], [*fragment(x / width, y / height, surf.get_at([x, y]))])
            # for x in range(width) for y in range(height)]
            # print(time.time() - t)
            surf.unlock()

            return surf

        # _color = self.text_box.value if self.text_box.value else 'red'
        return shader(w, h, _color)

    @staticmethod
    def slider_image(width, height):
        colors = [
            '#FF0000',
            '#FFFF00',
            '#00FF00',
            '#00FFFF',
            '#0000FF',
            '#FF00FF'
        ]
        color = pygame.Color(colors[0])
        increment = len(colors) / width
        i = 0
        val = 0
        s = pygame.Surface([width, height])
        while i <= width:
            next_color = colors[int(val + 1) % len(colors)]
            color = color.lerp(next_color, increment)
            pygame.draw.rect(s, color, [i, 0, 1, height])
            val += increment
            i += 1
        return s
