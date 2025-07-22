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

    pygame.draw.rect(win, brillo_color, (x, y, ancho, alto), border_radius=cfg.BUTTON_BORDER_RADIUS)
    pygame.draw.rect(win, color, (x+5, y+5, ancho-10, alto-10), border_radius=cfg.BUTTON_INNER_BORDER_RADIUS)
    pygame.draw.rect(win, cfg.BUTTON_BORDER_COLOR, (x, y, ancho, alto), cfg.BUTTON_BORDER_WIDTH, border_radius=cfg.BUTTON_BORDER_RADIUS)

    icono = text_cache.get_text(cfg.BUTTON_ICONS[columna], fuente_grande, cfg.BUTTON_ICON_COLOR)
    win.blit(icono, (x + ancho//2 - icono.get_width()//2, y + alto//2 - icono.get_height()//2))

def draw_note(win, x, y, color, alpha=255):
    temp_surf = pygame.Surface((cfg.NOTE_WIDTH, cfg.NOTE_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(temp_surf, (*color, alpha), (0, 0, cfg.NOTE_WIDTH, cfg.NOTE_HEIGHT), border_radius=cfg.NOTE_BORDER_RADIUS)
    pygame.draw.rect(temp_surf, (255, 255, 255, alpha), (0, 0, cfg.NOTE_WIDTH, cfg.NOTE_HEIGHT), cfg.NOTE_BORDER_WIDTH, border_radius=cfg.NOTE_BORDER_RADIUS)
    pygame.draw.circle(temp_surf, (255, 255, 255, alpha//2), (100, 15), cfg.NOTE_CIRCLE_RADIUS)
    win.blit(temp_surf, (x, y))

def draw_hit_evaluation(win, evaluation):
    if evaluation:
        color = cfg.HIT_EVALUATION_COLORS.get(evaluation, (255, 255, 255))
        text = text_cache.get_text(evaluation.upper(), fuente_grande, color)
        win.blit(text, (cfg.WIDTH//2 - text.get_width()//2, cfg.HIT_EVALUATION_Y))

def draw_game(win, game, teclas, glow_surface):
    win.fill(cfg.BACKGROUND_COLOR)

    glow_surface.fill((0, 0, 0, 0))
    for i in range(4):
        if teclas[i]:
            center_x = i * cfg.COLUMN_WIDTH + cfg.COLUMN_WIDTH // 2
            center_y = cfg.HIT_ZONE_Y - 50
            for r in range(cfg.NOTE_HIT_GLOW_RADIUS, 0, -5):
                alpha = cfg.NOTE_HIT_GLOW_ALPHA - r * 4
                gfxdraw.filled_circle(
                    glow_surface,
                    center_x,
                    center_y,
                    r,
                    (*cfg.COLORES[i], max(0, alpha)))
    win.blit(glow_surface, (0, 0))

    for i in range(1, 4):
        pygame.draw.line(win, cfg.LINE_COLOR, (i * cfg.COLUMN_WIDTH, 0), (i * cfg.COLUMN_WIDTH, cfg.HEIGHT), cfg.LINE_WIDTH)

    for nota in game.notas:
        if nota.activa:
            x = nota.columna * cfg.COLUMN_WIDTH + (cfg.COLUMN_WIDTH - cfg.NOTE_X_OFFSET) // 2
            draw_note(win, x, nota.y, nota.color, nota.alpha)

    pygame.draw.line(win, cfg.HIT_ZONE_COLOR, (0, cfg.HIT_ZONE_Y), (cfg.WIDTH, cfg.HIT_ZONE_Y), cfg.HIT_ZONE_LINE_WIDTH)
    for i in range(3):
        pygame.draw.line(win, (*cfg.HIT_ZONE_COLOR, 100 - i*30),
                        (0, cfg.HIT_ZONE_Y - i), (cfg.WIDTH, cfg.HIT_ZONE_Y - i), cfg.HIT_ZONE_NEON_WIDTH)
        pygame.draw.line(win, (*cfg.HIT_ZONE_COLOR, 100 - i*30),
                        (0, cfg.HIT_ZONE_Y + i), (cfg.WIDTH, cfg.HIT_ZONE_Y + i), cfg.HIT_ZONE_NEON_WIDTH)

    for i in range(4):
        draw_button(
            win,
            i * cfg.COLUMN_WIDTH + (cfg.COLUMN_WIDTH - cfg.BUTTON_WIDTH) // 2,
            cfg.HIT_ZONE_Y - cfg.BUTTON_Y_OFFSET,
            cfg.BUTTON_WIDTH,
            cfg.BUTTON_HEIGHT,
            cfg.COLORES[i],
            teclas[i],
            i
        )

    for anim in game.animations:
        anim.draw(win)

    pygame.draw.rect(win, cfg.PANEL_COLOR, (0, 0, cfg.WIDTH, cfg.PANEL_HEIGHT))
    pygame.draw.line(win, cfg.PANEL_LINE_COLOR, (0, cfg.PANEL_HEIGHT), (cfg.WIDTH, cfg.PANEL_HEIGHT), cfg.LINE_WIDTH)

    titulo = text_cache.get_text(cfg.GAME_TITLE, titulo_font, cfg.TITLE_COLOR)
    win.blit(titulo, (cfg.WIDTH//2 - titulo.get_width()//2, 20))

    texto_puntaje = text_cache.get_text(f"Puntaje: {game.puntaje}", fuente, cfg.SCORE_TEXT_COLOR)
    win.blit(texto_puntaje, (cfg.SCORE_X_OFFSET, 100))

    texto_nivel = text_cache.get_text(f"Nivel: {game.nivel}", fuente, cfg.LEVEL_TEXT_COLOR)
    win.blit(texto_nivel, (cfg.WIDTH - cfg.LEVEL_X_OFFSET, 100))

    if game.combo > 0:
        combo_color = cfg.COMBO_TEXT_COLOR_1 if game.combo < cfg.COMBO_FEVER_THRESHOLD else cfg.COMBO_TEXT_COLOR_2
        combo_text = text_cache.get_text(f"{game.combo}x COMBO!", fuente_grande, combo_color)
        win.blit(combo_text, (cfg.WIDTH//2 - combo_text.get_width()//2, 100))

    vida_text = text_cache.get_text(cfg.LIFE_TEXT, fuente, cfg.LIFE_COLOR)
    win.blit(vida_text, (cfg.WIDTH - cfg.LIFE_X_OFFSET, 100))
    for i in range(game.vidas):
        pygame.draw.circle(win, cfg.LIFE_COLOR, (cfg.WIDTH - 250 + i * cfg.LIFE_SPACING, cfg.LIFE_Y_OFFSET), 15)

    instrucciones = text_cache.get_text(cfg.INSTRUCTIONS_TEXT, fuente, cfg.INSTRUCTIONS_COLOR)
    win.blit(instrucciones, (cfg.WIDTH//2 - instrucciones.get_width()//2, cfg.HEIGHT - cfg.INSTRUCTIONS_Y_OFFSET))

    if game.last_hit_evaluation:
        draw_hit_evaluation(win, game.last_hit_evaluation)

    if game.combo > cfg.FEVER_MODE_THRESHOLD:
        pulse = abs(math.sin(time.time() * 5)) * 100
        overlay = pygame.Surface((cfg.WIDTH, cfg.HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (*cfg.COMBO_TEXT_COLOR_1, int(pulse//3)), (0, 0, cfg.WIDTH, cfg.HEIGHT))
        win.blit(overlay, (0, 0))

    if not game.juego_activo:
        overlay = pygame.Surface((cfg.WIDTH, cfg.HEIGHT), pygame.SRCALPHA)
        overlay.fill(cfg.GAME_OVER_BG_COLOR)
        win.blit(overlay, (0, 0))

        fin_text = text_cache.get_text(cfg.GAME_OVER_MESSAGE, titulo_font, cfg.GAME_OVER_TEXT_COLOR)
        win.blit(fin_text, (cfg.WIDTH//2 - fin_text.get_width()//2, cfg.HEIGHT//2 - cfg.GAME_OVER_Y_OFFSET))

        puntaje_final = text_cache.get_text(f"Puntaje final: {game.puntaje}", fuente_grande, cfg.FINAL_SCORE_COLOR)
        win.blit(puntaje_final, (cfg.WIDTH//2 - puntaje_final.get_width()//2, cfg.HEIGHT//2 + cfg.FINAL_SCORE_Y_OFFSET))

        max_combo_text = text_cache.get_text(f"Combo máximo: {game.max_combo}x", fuente_grande, cfg.MAX_COMBO_COLOR)
        win.blit(max_combo_text, (cfg.WIDTH//2 - max_combo_text.get_width()//2, cfg.HEIGHT//2 + cfg.MAX_COMBO_Y_OFFSET))

        reiniciar_text = text_cache.get_text(cfg.RESTART_MESSAGE, fuente, cfg.RESTART_TEXT_COLOR)
        win.blit(reiniciar_text, (cfg.WIDTH//2 - reiniciar_text.get_width()//2, cfg.HEIGHT//2 + cfg.RESTART_Y_OFFSET))

    pygame.display.flip()
