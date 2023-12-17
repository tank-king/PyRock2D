import asyncio
import os.path
from tkinter.filedialog import asksaveasfilename

import pygame.display

from src.app import RockApp
from src.dialog_box import *
from src.globals import Globals
from src.ui import *

pygame.init()


class Editor:
    def __init__(self):
        self.screen = pygame.display.set_mode([Config.W, Config.H], pygame.RESIZABLE)
        # self.window = Window.from_display_module()
        # self.window.maximize()
        pygame.display.set_caption('PyRock2D')
        pygame.display.set_icon(pygame.image.load(Config.ASSETS / 'images' / 'icon.png'))
        pygame.key.set_repeat(500, 25)
        self.clock = pygame.time.Clock()
        self.rock_app = RockApp()
        self.angle_spin_box = SpinBoxNumeric(0, 360, action=self.change_angle)
        self.light = pygame.image.load(Config.ASSETS / 'images' / 'light.png')

        self.objects = [
            self.rock_app,
            # Button('create', None),
            Button('Generate', action=self.rock_app.generate_rock),
            Button('Settings', action=self.settings),
            Button('Export', action=self.export),
            # Button('.json', None),
            self.angle_spin_box
        ]
        self.order_buttons()
        self.light_edited_once = False
        # self.grab_cursor = pygame.Cursor((12, 12),
        #                                  pygame.transform.smoothscale(pygame.image.load(
        #                                      os.path.join('.', 'assets', 'images', 'cursor-drag.png')), [32, 32]))

    def change_angle(self):
        Globals.ROCK_ANGLE = self.angle_spin_box.value

    def export(self):
        box = CustomDialogBox(
            'export',
            json=Button('.json', action=self.export_json),
            png=Button('.png', action=self.export_png)
        )
        box.show()

    def export_json(self):
        files = [('JSON', '*.json')]
        filename = asksaveasfilename(filetypes=files, defaultextension='.json')
        if filename:
            self.rock_app.export_json(filename)

    def export_png(self):
        filename = asksaveasfilename(filetypes=[('PNG', '*.png')], defaultextension='.png')
        if filename:
            self.rock_app.export_png(filename)

    def settings(self):
        b = Button('save', action=lambda: [b.__setattr__('saved', True)])
        b.saved = False
        box = CustomDialogBox(
            'Settings',
            width=SpinBoxNumeric(0, Globals.SCREEN_WIDTH, self.rock_app.rect.w),
            height=SpinBoxNumeric(0, Globals.SCREEN_HEIGHT, self.rock_app.rect.h),
            points=SpinBoxNumeric(0, 1000, Globals.ROCK_POINTS),
            color=ColorPicker(250, 150, initial_values=Globals.SLIDER_COORDS),
            save=b
        )
        result = box.show()
        w, h, p, c, button = result
        saved = button.saved
        if saved:
            Globals.ROCK_WIDTH = w.value
            Globals.ROCK_HEIGHT = h.value
            Globals.ROCK_POINTS = p.value
            Globals.ROCK_COLOR = c.value
            Globals.SLIDER_COORDS = c.slider_coords
        # return result

    def order_buttons(self):
        padding = 10, 10
        x = padding[0]
        for i in self.objects:
            if isinstance(i, UI):
                i.rect.topleft = [x, padding[1]]
                x += i.rect.w + 5

    def handle_lighting_pos(self, surf: pygame.Surface):
        if not Globals.LIGHTING:
            return
        if not self.light_edited_once:
            Globals.LIGHT_COORD = self.rock_app.rect.topleft
        mx, my = pygame.mouse.get_pos()
        clicked = pygame.mouse.get_pressed()[0]
        right_clicked = pygame.mouse.get_pressed()[2]
        rect = self.light.get_rect().scale_by(0.2)
        rect.center = mx, my
        if hovered := rect.collidepoint(Globals.LIGHT_COORD):
            self.rock_app.post(Events.MOUSE_HOVERED)

        if clicked:
            if hovered:
                Globals.LIGHTING_MOVE = True
                self.light_edited_once = True
            if Globals.LIGHTING_MOVE:
                # self.rock_app.post(Events.MOUSE_GRAB)
                Globals.LIGHT_COORD = [mx, my]
        else:
            Globals.LIGHTING_MOVE = False
        if not hovered and not clicked:
            Globals.LIGHTING_MOVE = False

        if right_clicked:
            self.light_edited_once = True
            Globals.LIGHT_COORD = [mx, my]

        surf.blit(self.light, self.light.get_rect(center=Globals.LIGHT_COORD))

    # @staticmethod
    def handle_events(self, events):
        mouse_hovered = False
        mouse_clicked = pygame.mouse.get_pressed()[0]
        for e in events:
            # if e.type == pygame.KEYDOWN:
            #     if e.key == pygame.K_ESCAPE:
            #         return False
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.WINDOWRESIZED:
                Config.W, Config.H = e.x, e.y
            if e.type == Events.MOUSE_HOVERED:
                mouse_hovered = True
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_l:
                    Globals.LIGHTING = not Globals.LIGHTING
        if mouse_hovered:
            # if mouse_clicked:
            #     pygame.mouse.set_cursor(self.grab_cursor)
            # else:
            if pygame.mouse.get_cursor() != pygame.SYSTEM_CURSOR_HAND:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            if pygame.mouse.get_cursor() != pygame.SYSTEM_CURSOR_ARROW:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        return True

    async def run(self):
        dt = 1
        while True:
            # Config.BG_COLOR = pygame.Color(Globals.ROCK_COLOR).lerp('black', 0.9)
            # print(Config.BG_COLOR)
            events = pygame.event.get()
            if not self.handle_events(events):
                return
            self.screen.fill(Config.BG_COLOR)
            # self.title_bar(events, self.screen)
            for i in self.objects:
                i.update(events, dt)
            for i in self.objects:
                i.draw(self.screen)
            self.handle_lighting_pos(self.screen)
            pygame.display.update()
            await asyncio.sleep(0)
            try:
                dt = Config.TARGET_FPS * self.clock.tick(Config.FPS) / 1000
            except ZeroDivisionError:
                dt = 1
            dt = pygame.math.clamp(dt, 0.01, 10)
