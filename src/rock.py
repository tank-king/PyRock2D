import random

import pygame

try:
    from scipy.spatial import ConvexHull, Delaunay
except (ModuleNotFoundError, ImportError):
    pass

from src.globals import BaseStructure, Globals

import pygame.gfxdraw


class Point(pygame.Vector2):
    pass


class Rock(BaseStructure):
    def __init__(self, width, height, num_points, position=None, scale=1.0):
        self.points = self.generate_rock_points(width, height, num_points)
        self.tri = Delaunay(self.points)
        self.outer_points = self.generate_outer_body(self.points)
        self.angle = 0
        self.pos = Point(0, 0) if position is None else position
        self.rel_dimensions = [0, 0]
        self.scale = scale
        self.size = [width, height]

    @staticmethod
    def generate_rock_points(width, height, num_points):
        random.seed()
        points = [Point(random.randint(-width // 2, width // 2), random.randint(-height // 2, height // 2)) for _ in
                  range(num_points - 4)]
        points.append(points[0])
        points.append(Point(random.randint(-width // 2, width // 2), -height // 2))
        points.append(Point(random.randint(-width // 2, width // 2), height // 2))
        points.append(Point(-width // 2, random.randint(-height // 2, height // 2)))
        points.append(Point(width // 2, random.randint(-height // 2, height // 2)))
        return points

    @staticmethod
    def generate_outer_body(points):
        hull = ConvexHull(points)
        hull_vertices = hull.vertices
        convex_hull_points = [points[i] for i in hull_vertices]
        return convex_hull_points

    @staticmethod
    def get_random_range(x, y=None):
        if y is None:
            y = x
            x = -x
        return random.randint(x, y)

    def draw(self, screen: pygame.Surface):
        if not Globals.LIGHTING:
            points = [Point(i).rotate(self.angle) + self.pos for i in self.outer_points]
            pygame.draw.polygon(screen, 'black', points)
            return
        points = [i.rotate(self.angle) + self.pos for i in self.points]
        s = pygame.Surface([Globals.ROCK_WIDTH, Globals.ROCK_HEIGHT])
        s = pygame.transform.rotate(s, self.angle)
        self.rel_dimensions = [*s.get_rect().size]
        mouse_pos = Point(*Globals.LIGHT_COORD)
        for simplex in self.tri.simplices:
            d = [points[i].distance_to(mouse_pos) for i in simplex]
            k = 255 - min(d) / 4
            k = pygame.math.clamp(k, 0, 255)
            k = k / 255
            color = pygame.Color(Globals.ROCK_COLOR)
            r = int(color.r * k)
            g = int(color.g * k)
            b = int(color.b * k)
            color.update(r, g, b)
            pygame.draw.polygon(screen, color, [points[i] for i in simplex])
