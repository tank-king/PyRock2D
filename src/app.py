import json

import pygame

from src.globals import BaseStructure, Config, Globals
from pygame.math import clamp

from src.rock import Rock, Point


class App(BaseStructure):
    """
    A virtual App (used like a Scene)
    """

    def __init__(self, name, rel_rect):
        self.rect = pygame.Rect(*rel_rect)
        self.name = name
        self.center_focused = False

    def resize_to(self, width, height):
        self.rect.width = width
        self.rect.height = height

    def get_mouse_position(self):
        mx, my = pygame.mouse.get_pos()
        return mx - self.rect.x, my - self.rect.y

    def update(self, events: list[pygame.event.Event], dt):
        if self.center_focused:
            pos = pygame.Vector2(*self.rect.topleft)
            target_pos = pygame.Vector2(Config.W // 2, Config.H // 2) - [self.rect.w // 2, self.rect.h // 2]
            topleft = pos.lerp(target_pos, clamp(0.1 * dt, 0, 1))
            self.rect.x = topleft.x
            self.rect.y = topleft.y

    def draw(self, screen: pygame.Surface):
        padding = 100
        pygame.draw.rect(screen, 'white', self.rect.inflate(padding, padding), 1, border_radius=5)


class RockApp(App):
    def __init__(self):
        super().__init__('rock app', [-100, -100, Globals.ROCK_WIDTH, Globals.ROCK_HEIGHT])
        self.center_focused = True
        self.rock = None
        self.generate_rock()

    def export_png(self, filename):
        rect = pygame.Rect(0, 0, *self.rock.rel_dimensions).scale_by(1)
        surf = pygame.Surface([*rect.size], pygame.SRCALPHA)
        surf.fill(Config.BG_COLOR)
        surf.set_colorkey(Config.BG_COLOR)
        screen = pygame.display.get_surface()
        screen.fill(Config.BG_COLOR)
        self.rock.draw(screen)
        surf.blit(screen, screen.get_rect(center=surf.get_rect().center))
        pygame.image.save(surf, filename, 'png')

    def export_json(self, filename):
        points = [[*Point(i).rotate(self.rock.angle)] for i in self.rock.points]
        simplices = [[int(j) for j in i] for i in self.rock.tri.simplices]
        # print(type(simplices), type(simplices[0][0]))
        data = {
            'points': points,
            'simplices': simplices,
            'size': self.rock.size,
            'angle': self.rock.angle
        }
        with open(filename, 'w') as f:
            f.write(json.dumps(data, indent=2))

    def generate_rock(self):
        self.rock = Rock(Globals.ROCK_WIDTH, Globals.ROCK_HEIGHT, Globals.ROCK_POINTS, self.rect.center)

    def update(self, events: list[pygame.event.Event], dt):
        super().update(events, dt)
        # self.rock.angle += dt
        # self.rock.angle %= 360
        self.rock.angle = Globals.ROCK_ANGLE
        self.rock.update(events, dt)
        self.resize_to(*self.rock.rel_dimensions)
        self.rock.pos = self.rect.center

    def draw(self, screen: pygame.Surface):
        if not Globals.LIGHTING_MOVE:
            super().draw(screen)
        self.rock.draw(screen)
