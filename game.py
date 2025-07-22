import pygame
import time
import random
from config import *
from note import Note
from animations import Explosion, Wave

class Game:
    def __init__(self):
        self.notas = []
        self.animations = []
        self.vidas = INITIAL_LIVES
        self.puntaje = INITIAL_SCORE
        self.fallos_seguidos = 0
        self.juego_activo = True
        self.combo = 0
        self.max_combo = 0
        self.nivel = 1
        self.tiempo_juego = 0
        self.tiempo_ultima_nota = 0
        self.ultima_penalizacion = 0
        self.pulsaciones_innecesarias = 0
        self.tiempo_inicio = time.time()

    def reiniciar_juego(self):
        self.notas = []
        self.animations = []
        self.vidas = INITIAL_LIVES
        self.puntaje = INITIAL_SCORE
        self.fallos_seguidos = 0
        self.juego_activo = True
        self.combo = 0
        self.max_combo = 0
        self.nivel = 1
        self.tiempo_juego = 0
        self.tiempo_inicio = time.time()

    def generate_note(self):
        columna = random.randint(0, 3)

        if self.notas and self.notas[-1].tipo == NOTE_TYPE_LONG:
            tipo = NOTE_TYPE_NORMAL
        else:
            tipo = random.choices([NOTE_TYPE_NORMAL, NOTE_TYPE_LONG], weights=[v for k,v in NOTE_PROBABILITIES.items()])[0]

        if tipo == NOTE_TYPE_NORMAL:
            return Note(columna)
        else:
            duracion = random.randint(*LONG_NOTE_DURATION_RANGE)
            return Note(columna, NOTE_TYPE_LONG, duracion)

    def update(self, teclas, dt):
        if not self.juego_activo:
            return

        ahora = time.time()
        self.tiempo_juego = ahora - self.tiempo_inicio
        self.nivel = max(1, min(MAX_LEVEL, int(self.tiempo_juego // DIFFICULTY_INCREASE_INTERVAL + 1)))

        intervalo_notas = max(0.2, NOTE_INTERVAL - self.nivel * NOTE_INTERVAL_DECREASE_RATE)
        velocidad_base = min(12, NOTE_SPEED + self.nivel * NOTE_SPEED_INCREASE_RATE)

        if ahora - self.tiempo_ultima_nota > intervalo_notas:
            self.notas.append(self.generate_note())
            self.tiempo_ultima_nota = ahora

        for nota in self.notas[:]:
            nota.velocidad = velocidad_base
            nota.update(dt)

            if not nota.activa:
                self.notas.remove(nota)
                continue

            if nota.is_hittable():
                if teclas[nota.columna]:
                    self.handle_hit(nota)
                elif nota.tipo == NOTE_TYPE_LONG:
                    pass

            if nota.tipo == NOTE_TYPE_LONG and nota.activa:
                if nota.y < HIT_ZONE_Y + 100 and teclas[nota.columna]:
                    avance = velocidad_base / nota.duracion
                    nota.progreso += avance
                    nota.progreso = min(nota.progreso, 1.0)

                    if nota.progreso >= 1.0 and not nota.larga_completada:
                        self.handle_long_note_completion(nota)

            elif nota.is_offscreen():
                self.handle_miss()
                self.notas.remove(nota)

        for i in range(4):
            if teclas[i]:
                nota_cercana = False
                for nota in self.notas:
                    if nota.columna == i and abs(nota.y - HIT_ZONE_Y) < 150:
                        nota_cercana = True
                        break

                if not nota_cercana and ahora - self.ultima_penalizacion > 0.1:
                    self.puntaje -= WRONG_HIT_PENALTY
                    self.pulsaciones_innecesarias += 1
                    self.ultima_penalizacion = ahora

        for anim in self.animations[:]:
            anim.update(dt)
            if anim.completed:
                self.animations.remove(anim)

    def handle_hit(self, nota):
        nota.activa = False
        self.combo += 1
        self.max_combo = max(self.max_combo, self.combo)
        self.fallos_seguidos = 0
        self.puntaje += HIT_REWARD * self.combo

        self.animations.append(Explosion(
            nota.columna * COLUMN_WIDTH + COLUMN_WIDTH // 2,
            nota.y,
            nota.color
        ))

        if nota.tipo == NOTE_TYPE_LONG:
            self.animations.append(Wave(
                nota.columna * COLUMN_WIDTH + COLUMN_WIDTH // 2,
                nota.y,
                nota.color
            ))

        if nota in self.notas:
            self.notas.remove(nota)

    def handle_long_note_completion(self, nota):
        nota.larga_completada = True
        nota.activa = False
        self.puntaje += LONG_NOTE_REWARD
        self.animations.append(Wave(
            nota.columna * COLUMN_WIDTH + COLUMN_WIDTH // 2,
            nota.y + nota.duracion,
            (255, 255, 255)
        ))

    def handle_miss(self):
        self.combo = 0
        self.puntaje -= MISS_PENALTY
        self.vidas -= 1
        if self.vidas <= 0:
            self.juego_activo = False
