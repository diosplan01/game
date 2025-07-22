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
        self.duracion = duracion if tipo == NOTE_TYPE_LONG else 0
        self.progreso = 0  # For long notes
        self.color = COLORES[columna]
        self.alpha = 255
        self.creado = time.time()
        self.larga_completada = False

    def move(self):
        self.y += self.velocidad

    def update(self):
        self.move()
        if self.y > ZONA_GOLPEO_Y + 100:
            self.alpha = max(0, self.alpha - 5)
            if self.alpha <= 0:
                self.activa = False

    def is_hittable(self):
        return abs(self.y - ZONA_GOLPEO_Y) < 30

    def is_offscreen(self):
        return self.y > ZONA_GOLPEO_Y + 100

def generate_note(notas):
    columna = random.randint(0, 3)

    if notas and notas[-1].tipo == NOTE_TYPE_LONG:
        tipo = NOTE_TYPE_NORMAL
    else:
        tipo = random.choices([NOTE_TYPE_NORMAL, NOTE_TYPE_LONG], weights=[75, 25])[0]

    if tipo == NOTE_TYPE_NORMAL:
        return Note(columna)
    else:
        duracion = random.randint(*LONG_NOTE_DURATION_RANGE)
        return Note(columna, NOTE_TYPE_LONG, duracion)
