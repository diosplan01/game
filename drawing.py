import pygame
import time
import math
from pygame import gfxdraw
import config as cfg

# Fonts
pygame.font.init()
titulo_font = pygame.font.SysFont(cfg.FONT_NAME, cfg.TITLE_FONT_SIZE, bold=True)
fuente_grande = pygame.font.SysFont(cfg.FONT_NAME, cfg.LARGE_FONT_SIZE, bold=True)
fuente = pygame.font.SysFont(cfg.FONT_NAME, cfg.DEFAULT_FONT_SIZE)

class TextCache:
    def __init__(self):
        self.cache = {}

    def get_text(self, text, font, color):
        if (text, font, color) not in self.cache:
            self.cache[(text, font, color)] = font.render(text, True, color)
        return self.cache[(text, font, color)]

text_cache = TextCache()

def draw_button(win, x, y, ancho, alto, color, presionado, columna):
    if presionado:
        brillo_color = (min(color[0]+100, 255), min(color[1]+100, 255), min(color[2]+100, 255))
    else:
        brillo_color = (min(color[0]+50, 255), min(color[1]+50, 255), min(color[2]+50, 255))

    pygame.draw.rect(win, brillo_color, (x, y, ancho, alto), border_radius=15)
    pygame.draw.rect(win, color, (x+5, y+5, ancho-10, alto-10), border_radius=12)
    pygame.draw.rect(win, cfg.BUTTON_BORDER_COLOR, (x, y, ancho, alto), 3, border_radius=15)

    icono = text_cache.get_text(cfg.BUTTON_ICONS[columna], fuente_grande, cfg.BUTTON_ICON_COLOR)
    win.blit(icono, (x + ancho//2 - icono.get_width()//2, y + alto//2 - icono.get_height()//2))

def draw_note_normal(win, x, y, color, alpha=255):
    temp_surf = pygame.Surface((cfg.NOTE_WIDTH, cfg.NOTE_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(temp_surf, (*color, alpha), (0, 0, cfg.NOTE_WIDTH, cfg.NOTE_HEIGHT), border_radius=10)
    pygame.draw.rect(temp_surf, (255, 255, 255, alpha), (0, 0, cfg.NOTE_WIDTH, cfg.NOTE_HEIGHT), 2, border_radius=10)
    pygame.draw.circle(temp_surf, (255, 255, 255, alpha//2), (100, 15), 10)
    win.blit(temp_surf, (x, y))

def draw_note_larga(win, x, y, altura, color, progreso=0.0):
    restante = altura * (1.0 - progreso)
    y_inicio = max(0, int(y + altura * progreso))
    y_fin = min(int(y + altura), cfg.HEIGHT)

    if y_fin <= y_inicio:
        return

    for i in range(y_inicio, y_fin):
        rel_pos = i - y
        alpha = max(0, 255 - int((rel_pos / altura) * 155))
        color_actual = (*color, alpha)
        pygame.draw.rect(win, color_actual, (x, i, 100, 1))

    if y_inicio < cfg.HEIGHT:
        pygame.draw.rect(win, color, (x - 10, y_inicio - 15, 120, 15), border_radius=7)
        pygame.draw.rect(win, (255, 255, 255), (x - 10, y_inicio - 15, 120, 15), 2, border_radius=7)

    if y + altura < cfg.HEIGHT + 30:
        pygame.draw.rect(win, color, (x - 10, y + altura - 15, 120, 15), border_radius=7)
        pygame.draw.rect(win, (255, 255, 255), (x - 10, y + altura - 15, 120, 15), 2, border_radius=7)

def draw_game(win, game, teclas, glow_surface):
    win.fill(cfg.BACKGROUND_COLOR)

    glow_surface.fill((0, 0, 0, 0))
    for i in range(4):
        if teclas[i]:
            center_x = i * cfg.COLUMN_WIDTH + cfg.COLUMN_WIDTH // 2
            center_y = cfg.HIT_ZONE_Y - 50
            for r in range(30, 0, -5):
                alpha = 150 - r * 4
                gfxdraw.filled_circle(
                    glow_surface,
                    center_x,
                    center_y,
                    r,
                    (*cfg.COLORES[i], max(0, alpha)))
    win.blit(glow_surface, (0, 0))

    for i in range(1, 4):
        pygame.draw.line(win, cfg.LINE_COLOR, (i * cfg.COLUMN_WIDTH, 0), (i * cfg.COLUMN_WIDTH, cfg.HEIGHT), 2)

    for nota in game.notas:
        if nota.activa:
            x = nota.columna * cfg.COLUMN_WIDTH + (cfg.COLUMN_WIDTH - 120) // 2
            if nota.tipo == 'normal':
                draw_note_normal(win, x, nota.y, nota.color, nota.alpha)
            else:
                draw_note_larga(win, x, nota.y, nota.duracion, nota.color, nota.progreso)

    pygame.draw.line(win, cfg.HIT_ZONE_COLOR, (0, cfg.HIT_ZONE_Y), (cfg.WIDTH, cfg.HIT_ZONE_Y), 3)
    for i in range(3):
        pygame.draw.line(win, (*cfg.HIT_ZONE_COLOR, 100 - i*30),
                        (0, cfg.HIT_ZONE_Y - i), (cfg.WIDTH, cfg.HIT_ZONE_Y - i), 1)
        pygame.draw.line(win, (*cfg.HIT_ZONE_COLOR, 100 - i*30),
                        (0, cfg.HIT_ZONE_Y + i), (cfg.WIDTH, cfg.HIT_ZONE_Y + i), 1)

    for i in range(4):
        draw_button(
            win,
            i * cfg.COLUMN_WIDTH + (cfg.COLUMN_WIDTH - 150) // 2,
            cfg.HIT_ZONE_Y - 80,
            150,
            80,
            cfg.COLORES[i],
            teclas[i],
            i
        )

    for anim in game.animations:
        anim.draw(win)

    pygame.draw.rect(win, cfg.PANEL_COLOR, (0, 0, cfg.WIDTH, 150))
    pygame.draw.line(win, cfg.PANEL_LINE_COLOR, (0, 150), (cfg.WIDTH, 150), 2)

    titulo = text_cache.get_text(cfg.GAME_TITLE, titulo_font, cfg.TITLE_COLOR)
    win.blit(titulo, (cfg.WIDTH//2 - titulo.get_width()//2, 20))

    texto_puntaje = text_cache.get_text(f"Puntaje: {game.puntaje}", fuente, cfg.SCORE_TEXT_COLOR)
    win.blit(texto_puntaje, (50, 100))

    texto_nivel = text_cache.get_text(f"Nivel: {game.nivel}", fuente, cfg.LEVEL_TEXT_COLOR)
    win.blit(texto_nivel, (cfg.WIDTH - 200, 100))

    if game.combo > 0:
        combo_color = cfg.COMBO_TEXT_COLOR_1 if game.combo < 30 else cfg.COMBO_TEXT_COLOR_2
        combo_text = text_cache.get_text(f"{game.combo}x COMBO!", fuente_grande, combo_color)
        win.blit(combo_text, (cfg.WIDTH//2 - combo_text.get_width()//2, 100))

    vida_text = text_cache.get_text(cfg.LIFE_TEXT, fuente, cfg.LIFE_COLOR)
    win.blit(vida_text, (cfg.WIDTH - 350, 100))
    for i in range(game.vidas):
        pygame.draw.circle(win, cfg.LIFE_COLOR, (cfg.WIDTH - 250 + i*40, 115), 15)

    instrucciones = text_cache.get_text(cfg.INSTRUCTIONS_TEXT, fuente, cfg.INSTRUCTIONS_COLOR)
    win.blit(instrucciones, (cfg.WIDTH//2 - instrucciones.get_width()//2, cfg.HEIGHT - 30))

    if game.combo > cfg.FEVER_MODE_THRESHOLD:
        pulse = abs(math.sin(time.time() * 5)) * 100
        overlay = pygame.Surface((cfg.WIDTH, cfg.HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (255, 255, 100, int(pulse//3)), (0, 0, cfg.WIDTH, cfg.HEIGHT))
        win.blit(overlay, (0, 0))

    if not game.juego_activo:
        overlay = pygame.Surface((cfg.WIDTH, cfg.HEIGHT), pygame.SRCALPHA)
        overlay.fill(cfg.GAME_OVER_BG_COLOR)
        win.blit(overlay, (0, 0))

        fin_text = text_cache.get_text(cfg.GAME_OVER_MESSAGE, titulo_font, cfg.GAME_OVER_TEXT_COLOR)
        win.blit(fin_text, (cfg.WIDTH//2 - fin_text.get_width()//2, cfg.HEIGHT//2 - 80))

        puntaje_final = text_cache.get_text(f"Puntaje final: {game.puntaje}", fuente_grande, cfg.FINAL_SCORE_COLOR)
        win.blit(puntaje_final, (cfg.WIDTH//2 - puntaje_final.get_width()//2, cfg.HEIGHT//2))

        max_combo_text = text_cache.get_text(f"Combo máximo: {game.max_combo}x", fuente_grande, cfg.MAX_COMBO_COLOR)
        win.blit(max_combo_text, (cfg.WIDTH//2 - max_combo_text.get_width()//2, cfg.HEIGHT//2 + 60))

        reiniciar_text = text_cache.get_text(cfg.RESTART_MESSAGE, fuente, cfg.RESTART_TEXT_COLOR)
        win.blit(reiniciar_text, (cfg.WIDTH//2 - reiniciar_text.get_width()//2, cfg.HEIGHT//2 + 180))

    pygame.display.flip()
