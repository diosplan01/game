import pygame
from pygame import gfxdraw
from config import EXPLOSION_RADIUS, WAVE_RADIUS, ANIMATION_DURATION

class Animation:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.progress = 0.0
        self.completed = False

    def update(self, dt):
        raise NotImplementedError

    def draw(self, surface):
        raise NotImplementedError

class Explosion(Animation):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.radius = 5
        self.max_radius = EXPLOSION_RADIUS
        self.duration = ANIMATION_DURATION

    def update(self, dt):
        self.progress += dt / self.duration
        if self.progress >= 1.0:
            self.progress = 1.0
            self.completed = True

    def draw(self, surface):
        radius = self.radius + (self.max_radius - self.radius) * self.progress
        alpha = max(0, 255 - 255 * self.progress)

        if alpha > 0:
            gfxdraw.filled_circle(
                surface,
                int(self.x),
                int(self.y),
                int(radius),
                (*self.color, int(alpha)))

class Wave(Animation):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.radius = 10
        self.max_radius = WAVE_RADIUS
        self.duration = ANIMATION_DURATION

    def update(self, dt):
        self.progress += dt / self.duration
        if self.progress >= 1.0:
            self.progress = 1.0
            self.completed = True

    def draw(self, surface):
        radius = self.radius + (self.max_radius - self.radius) * self.progress
        alpha = max(0, 255 - 255 * self.progress)

        if alpha > 0:
            gfxdraw.filled_circle(
                surface,
                int(self.x),
                int(self.y),
                int(radius),
                (*self.color, int(alpha)))

            gfxdraw.aacircle(
                surface,
                int(self.x),
                int(self.y),
                int(radius),
                (*self.color, int(alpha)))
