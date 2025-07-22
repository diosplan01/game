import pygame
import time
from pygame import gfxdraw
from config import EXPLOSION_RADIUS, WAVE_RADIUS

class Animation:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.creado = time.time()
        self.completado = False

    def update(self):
        raise NotImplementedError

    def draw(self, surface):
        raise NotImplementedError

class Explosion(Animation):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.radius = 5
        self.max_radius = EXPLOSION_RADIUS

    def update(self):
        tiempo_transcurrido = time.time() - self.creado
        progreso = min(1.0, tiempo_transcurrido * 2)
        if progreso >= 1.0:
            self.completado = True

    def draw(self, surface):
        tiempo_transcurrido = time.time() - self.creado
        progreso = min(1.0, tiempo_transcurrido * 2)
        radio = self.radius + (self.max_radius - self.radius) * progreso
        alpha = max(0, 255 - 255 * progreso)

        if alpha > 0:
            gfxdraw.filled_circle(
                surface,
                int(self.x),
                int(self.y),
                int(radio),
                (*self.color, int(alpha)))

class Wave(Animation):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.radius = 10
        self.max_radius = WAVE_RADIUS

    def update(self):
        tiempo_transcurrido = time.time() - self.creado
        progreso = min(1.0, tiempo_transcurrido * 2)
        if progreso >= 1.0:
            self.completado = True

    def draw(self, surface):
        tiempo_transcurrido = time.time() - self.creado
        progreso = min(1.0, tiempo_transcurrido * 2)
        radio = self.radius + (self.max_radius - self.radius) * progreso
        alpha = max(0, 255 - 255 * progreso)

        if alpha > 0:
            gfxdraw.filled_circle(
                surface,
                int(self.x),
                int(self.y),
                int(radio),
                (*self.color, int(alpha)))

            gfxdraw.aacircle(
                surface,
                int(self.x),
                int(self.y),
                int(radio),
                (*self.color, int(alpha)))
