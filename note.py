import time
import random
from config import COLORES, NOTE_TYPE_NORMAL, NOTE_TYPE_LONG, LONG_NOTE_DURATION_RANGE, HIT_ZONE_Y, NOTE_SPEED

class Note:
    def __init__(self, columna, tipo=NOTE_TYPE_NORMAL, duracion=0):
        self.columna = columna
        self.tipo = tipo
        self.y = -100
        self.velocidad = NOTE_SPEED
        self.activa = True
        self.golpeada = False
        self.holding = False
        self.duracion = duracion if tipo == NOTE_TYPE_LONG else 0
        self.progreso = 0  # For long notes
        self.color = COLORES[columna]
        self.alpha = 255
        self.creado = time.time()
        self.larga_completada = False

    def move(self, dt):
        self.y += self.velocidad * dt * 60

    def update(self, dt, holding_key):
        self.move(dt)

        if self.tipo == NOTE_TYPE_LONG:
            if self.is_hittable() and holding_key and not self.holding:
                self.holding = True

            if self.holding:
                self.progreso += dt / (self.duracion / 1000.0)
                if self.progreso >= 1.0:
                    self.progreso = 1.0
                    self.larga_completada = True
                    self.activa = False
                if not holding_key:
                    self.activa = False # Missed the long note

        if self.y > HIT_ZONE_Y + 100:
            self.alpha = max(0, self.alpha - 5)
            if self.alpha <= 0:
                self.activa = False

    def is_hittable(self):
        return abs(self.y - HIT_ZONE_Y) < 30

    def is_offscreen(self):
        return self.y > HIT_ZONE_Y + 100
