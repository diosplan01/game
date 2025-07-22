import pygame
import serial
import threading
import time
import random
import sys
import math
from pygame import gfxdraw

# Configuración del puerto serie
try:
    ser = serial.Serial("COM4", 115200)
except serial.SerialException:
    print("No se pudo abrir el puerto serie.")
    ser = None

# Estado de las teclas físicas
teclas = [False] * 4
ultimo_pulso = [0] * 4
TIEMPO_TIMEOUT = 0.075

# Thread para leer del ESP32
def leer_serial():
    while True:
        if ser and ser.in_waiting:
            try:
                data = ser.readline().decode().strip()
                if data.isdigit():
                    i = int(data)
                    if 0 <= i < len(teclas):
                        teclas[i] = True
                        ultimo_pulso[i] = time.time()
            except Exception as e:
                print("Error al leer:", e)

if ser:
    hilo = threading.Thread(target=leer_serial, daemon=True)
    hilo.start()

# Inicializar Pygame
pygame.init()
WIDTH, HEIGHT = 1200, 800  # Pantalla más grande
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Peor que el tetris")
reloj = pygame.time.Clock()

# Crear una superficie para efectos de iluminación
glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

# Colores base con colores más vibrantes
COLORES = [
    (255, 100, 100),  # Rojo
    (100, 255, 100),  # Verde
    (100, 200, 255),  # Azul cielo
    (255, 255, 100)   # Amarillo
]

# Fuentes
titulo_font = pygame.font.SysFont("Arial", 64, bold=True)
fuente_grande = pygame.font.SysFont("Arial", 48, bold=True)
fuente = pygame.font.SysFont("Arial", 32)

# Variables del juego
class Nota:
    def __init__(self, columna, tipo='normal', duracion=0):
        self.columna = columna
        self.tipo = tipo  # 'normal' o 'larga'
        self.y = -100
        self.velocidad = 5
        self.activa = True
        self.golpeada = False
        self.duracion = duracion
        self.progreso = 0  # Para notas largas
        self.color = COLORES[columna]
        self.alpha = 255
        self.creado = time.time()
        self.larga_completada = False

notas = []
explosiones = []
tiempo_ultima_nota = 0
intervalo_notas = 0.8  # segundos entre notas
velocidad_base = 5
columna_ancho = WIDTH // 4

vidas = 3
puntaje = 1000  # Empezamos con 1000 puntos y vamos restando por errores
fallos_seguidos = 0
juego_activo = True
combo = 0
max_combo = 0
ZONA_GOLPEO_Y = HEIGHT - 200  # Zona más arriba
pulsaciones_innecesarias = 0
nivel = 1
tiempo_juego = 0

# Generar notas con mayor espacio entre largas y normales
def generar_nota():
    columna = random.randint(0, 3)
    
    # Disminuir probabilidad de notas largas consecutivas
    if notas and notas[-1].tipo == 'larga':
        tipo = 'normal'
    else:
        tipo = random.choices(['normal', 'larga'], weights=[75, 25])[0]
    
    if tipo == 'normal':
        notas.append(Nota(columna))
    else:
        duracion = random.randint(150, 300)  # Longitud de la nota larga
        notas.append(Nota(columna, 'larga', duracion))

def reiniciar_juego():
    global notas, explosiones, vidas, puntaje, fallos_seguidos, juego_activo, combo, max_combo, nivel, tiempo_juego
    notas = []
    explosiones = []
    vidas = 3
    puntaje = 1000
    fallos_seguidos = 0
    juego_activo = True
    combo = 0
    max_combo = 0
    nivel = 1
    tiempo_juego = 0

def crear_explosion(x, y, color):
    explosiones.append({
        'x': x,
        'y': y,
        'color': color,
        'radius': 5,
        'max_radius': 50,
        'creado': time.time()
    })

def crear_onda(x, y, color):
    explosiones.append({
        'x': x,
        'y': y,
        'color': color,
        'radius': 10,
        'max_radius': 100,
        'creado': time.time(),
        'tipo': 'onda'
    })

def dibujar_boton(x, y, ancho, alto, color, presionado, columna):
    # Dibujar brillo del botón
    if presionado:
        brillo_color = (min(color[0]+100, 255), min(color[1]+100, 255), min(color[2]+100, 255))
    else:
        brillo_color = (min(color[0]+50, 255), min(color[1]+50, 255), min(color[2]+50, 255))
    
    # Dibujar efecto de neón
    pygame.draw.rect(win, brillo_color, (x, y, ancho, alto), border_radius=15)
    
    # Dibujar botón principal
    pygame.draw.rect(win, color, (x+5, y+5, ancho-10, alto-10), border_radius=12)
    
    # Dibujar borde
    borde_color = (200, 200, 200, 150)
    pygame.draw.rect(win, borde_color, (x, y, ancho, alto), 3, border_radius=15)
    
    # Dibujar icono según columna
    iconos = ["+", "+", "+", "+"]
    icono = fuente_grande.render(iconos[columna], True, (255, 255, 255))
    win.blit(icono, (x + ancho//2 - icono.get_width()//2, y + alto//2 - icono.get_height()//2))

def dibujar_nota_normal(x, y, color, alpha=255):
    # Crear superficie temporal para efectos de transparencia
    temp_surf = pygame.Surface((120, 30), pygame.SRCALPHA)
    
    # Dibujar cuerpo de la nota
    pygame.draw.rect(temp_surf, (*color, alpha), (0, 0, 120, 30), border_radius=10)
    
    # Dibujar borde brillante
    pygame.draw.rect(temp_surf, (255, 255, 255, alpha), (0, 0, 120, 30), 2, border_radius=10)
    
    # Dibujar destello
    pygame.draw.circle(temp_surf, (255, 255, 255, alpha//2), (100, 15), 10)
    
    win.blit(temp_surf, (x, y))

def dibujar_nota_larga(x, y, altura, color, progreso=0.0):
    restante = altura * (1.0 - progreso)
    y_inicio = max(0, int(y + altura * progreso))
    y_fin = min(int(y + altura), HEIGHT)

    if y_fin <= y_inicio:
        return  # Ya se completó

    for i in range(y_inicio, y_fin):
        rel_pos = i - y
        alpha = max(0, 255 - int((rel_pos / altura) * 155))
        color_actual = (*color, alpha)
        pygame.draw.rect(win, color_actual, (x, i, 100, 1))

    # Cabecera (parte superior visible)
    if y_inicio < HEIGHT:
        pygame.draw.rect(win, color, (x - 10, y_inicio - 15, 120, 15), border_radius=7)
        pygame.draw.rect(win, (255, 255, 255), (x - 10, y_inicio - 15, 120, 15), 2, border_radius=7)

    # Cola
    if y + altura < HEIGHT + 30:
        pygame.draw.rect(win, color, (x - 10, y + altura - 15, 120, 15), border_radius=7)
        pygame.draw.rect(win, (255, 255, 255), (x - 10, y + altura - 15, 120, 15), 2, border_radius=7)


def dibujar():
    win.fill((20, 15, 30))  # Fondo oscuro
    
    # Dibujar efecto de iluminación en la zona de golpeo
    glow_surface.fill((0, 0, 0, 0))
    for i in range(4):
        if teclas[i]:
            # Efecto de brillo en el botón presionado
            center_x = i * columna_ancho + columna_ancho // 2
            center_y = ZONA_GOLPEO_Y - 50
            
            for r in range(30, 0, -5):
                alpha = 150 - r * 4
                pygame.gfxdraw.filled_circle(
                    glow_surface, 
                    center_x, 
                    center_y, 
                    r, 
                    (*COLORES[i], max(0, alpha)))
    
    win.blit(glow_surface, (0, 0))
    
    # Dibujar líneas divisorias
    for i in range(1, 4):
        pygame.draw.line(win, (60, 50, 80, 150), (i * columna_ancho, 0), (i * columna_ancho, HEIGHT), 2)
    
    # Dibujar notas
    for nota in notas:
        if nota.activa:
            x = nota.columna * columna_ancho + (columna_ancho - 120) // 2
            
            if nota.tipo == 'normal':
                dibujar_nota_normal(x, nota.y, nota.color, nota.alpha)
            else:  # Nota larga
                dibujar_nota_larga(
                    x, 
                    nota.y, 
                    nota.duracion, 
                    nota.color,
                    nota.progreso
                )
    
    # Dibujar línea de golpeo con efecto neón
    pygame.draw.line(win, (100, 200, 255), (0, ZONA_GOLPEO_Y), (WIDTH, ZONA_GOLPEO_Y), 3)
    
    # Dibujar efecto de neón en la línea
    for i in range(3):
        pygame.draw.line(win, (100, 200, 255, 100 - i*30), 
                        (0, ZONA_GOLPEO_Y - i), (WIDTH, ZONA_GOLPEO_Y - i), 1)
        pygame.draw.line(win, (100, 200, 255, 100 - i*30), 
                        (0, ZONA_GOLPEO_Y + i), (WIDTH, ZONA_GOLPEO_Y + i), 1)
    
    # Dibujar botones en la zona de golpeo
    for i in range(4):
        dibujar_boton(
            i * columna_ancho + (columna_ancho - 150) // 2, 
            ZONA_GOLPEO_Y - 80, 
            150, 
            80, 
            COLORES[i], 
            teclas[i],
            i
        )
    
    # Dibujar explosiones y ondas
    for exp in explosiones[:]:
        tiempo_transcurrido = time.time() - exp['creado']
        progreso = min(1.0, tiempo_transcurrido * 2)
        
        if 'tipo' in exp and exp['tipo'] == 'onda':
            radio = exp['radius'] + (exp['max_radius'] - exp['radius']) * progreso
            alpha = max(0, 255 - 255 * progreso)
            
            if alpha > 0:
                pygame.gfxdraw.filled_circle(
                    win, 
                    int(exp['x']), 
                    int(exp['y']), 
                    int(radio), 
                    (*exp['color'], int(alpha)))
                
                pygame.gfxdraw.aacircle(
                    win, 
                    int(exp['x']), 
                    int(exp['y']), 
                    int(radio), 
                    (*exp['color'], int(alpha)))
            else:
                explosiones.remove(exp)
        else:
            radio = exp['radius'] + (exp['max_radius'] - exp['radius']) * progreso
            alpha = max(0, 255 - 255 * progreso)
            
            if alpha > 0:
                pygame.gfxdraw.filled_circle(
                    win, 
                    int(exp['x']), 
                    int(exp['y']), 
                    int(radio), 
                    (*exp['color'], int(alpha)))
            else:
                explosiones.remove(exp)
    
    # Dibujar panel de información
    pygame.draw.rect(win, (30, 25, 40, 220), (0, 0, WIDTH, 150))
    pygame.draw.line(win, (80, 70, 100), (0, 150), (WIDTH, 150), 2)
    
    # Título
    titulo = titulo_font.render("Piano titles de la feria", True, (255, 200, 100))
    win.blit(titulo, (WIDTH//2 - titulo.get_width()//2, 20))
    
    # Información del juego
    texto_puntaje = fuente.render(f"Puntaje: {puntaje}", True, (255, 255, 255))
    win.blit(texto_puntaje, (50, 100))
    
    texto_nivel = fuente.render(f"Nivel: {nivel}", True, (200, 200, 255))
    win.blit(texto_nivel, (WIDTH - 200, 100))
    
    if combo > 0:
        combo_text = fuente_grande.render(f"{combo}x COMBO!", True, 
                                        (255, 255 - combo * 2, 100) if combo < 30 else (255, 100, 255))
        win.blit(combo_text, (WIDTH//2 - combo_text.get_width()//2, 100))
    
    # Vidas
    vida_text = fuente.render("Life:", True, (255, 100, 100))
    win.blit(vida_text, (WIDTH - 350, 100))
    for i in range(vidas):
        pygame.draw.circle(win, (255, 100, 100), (WIDTH - 250 + i*40, 115), 15)
    
    # Instrucciones
    instrucciones = fuente.render("Presiona cuando lleguen al recuadro", True, (200, 200, 255))
    win.blit(instrucciones, (WIDTH//2 - instrucciones.get_width()//2, HEIGHT - 30))
    
    # Efectos visuales para combo alto
    if combo > 20:
        pulse = abs(math.sin(time.time() * 5)) * 100
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (255, 255, 100, int(pulse//3)), (0, 0, WIDTH, HEIGHT))
        win.blit(overlay, (0, 0))
    
    if not juego_activo:
        # Fondo semitransparente
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        win.blit(overlay, (0, 0))
        
        fin_text = titulo_font.render("¡FIN DEL JUEGO!", True, (255, 100, 100))
        win.blit(fin_text, (WIDTH//2 - fin_text.get_width()//2, HEIGHT//2 - 80))
        
        puntaje_final = fuente_grande.render(f"Puntaje final: {puntaje}", True, (255, 255, 255))
        win.blit(puntaje_final, (WIDTH//2 - puntaje_final.get_width()//2, HEIGHT//2))
        
        max_combo_text = fuente_grande.render(f"Combo máximo: {max_combo}x", True, (100, 255, 255))
        win.blit(max_combo_text, (WIDTH//2 - max_combo_text.get_width()//2, HEIGHT//2 + 60))
        
        reiniciar_text = fuente.render("Presiona R para reiniciar", True, (200, 200, 100))
        win.blit(reiniciar_text, (WIDTH//2 - reiniciar_text.get_width()//2, HEIGHT//2 + 180))
    
    pygame.display.flip()

# Loop principal
corriendo = True
tiempo_inicio = time.time()
ultima_penalizacion = 0

while corriendo:
    tiempo_actual = time.time()
    tiempo_juego = tiempo_actual - tiempo_inicio
    nivel = max(1, min(10, int(tiempo_juego // 15 + 1)))
    
    reloj.tick(60)
    
    # Manejo de eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            corriendo = False
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_r and not juego_activo:
                reiniciar_juego()
                tiempo_inicio = time.time()
            if evento.key == pygame.K_ESCAPE:
                corriendo = False
    
    # Actualizar estado de teclas físicas
    ahora = time.time()
    for i in range(4):
        if teclas[i] and (ahora - ultimo_pulso[i]) > TIEMPO_TIMEOUT:
            teclas[i] = False
    
    if juego_activo:
        # Aumentar dificultad con el tiempo
        intervalo_notas = max(0.2, 0.8 - nivel * 0.06)
        velocidad_base = min(12, 5 + nivel * 0.7)
        
        # Generar nuevas notas
        if ahora - tiempo_ultima_nota > intervalo_notas:
            generar_nota()
            tiempo_ultima_nota = ahora
        
        # Mover notas y verificar golpeo
        for nota in notas[:]:
            if nota.activa:
                nota.y += velocidad_base
                
                # Efecto de desvanecimiento para notas que se van
                if nota.y > ZONA_GOLPEO_Y + 100:
                    nota.alpha = max(0, nota.alpha - 5)
                    if nota.alpha <= 0:
                        notas.remove(nota)
                        continue
                
                # Verificar si llegó a la zona de golpeo
                if abs(nota.y - ZONA_GOLPEO_Y) < 30:
                    if teclas[nota.columna]:
                        # Golpe exitoso
                        nota.activa = False
                        combo += 1
                        max_combo = max(max_combo, combo)
                        fallos_seguidos = 0
                        puntaje += 10 * combo  # Bonus por combo
                        
                        # Crear explosión visual
                        crear_explosion(
                            nota.columna * columna_ancho + columna_ancho // 2,
                            nota.y,
                            nota.color
                        )
                        
                        # Si es nota larga, crear onda expansiva
                        if nota.tipo == 'larga':
                            crear_onda(
                                nota.columna * columna_ancho + columna_ancho // 2,
                                nota.y,
                                nota.color
                            )
                        
                        # Eliminar nota
                        notas.remove(nota)
                    elif nota.tipo == 'larga':
                        # Para notas largas, verificar si se presiona durante su paso
                        pass
                
                # Manejo de notas largas
                if nota.tipo == 'larga' and nota.activa:
                    # Calcular progreso de la nota larga
                    if nota.y < ZONA_GOLPEO_Y + 100 and teclas[nota.columna]:
                        avance = velocidad_base / nota.duracion
                        nota.progreso += avance
                        nota.progreso = min(nota.progreso, 1.0)

                        if nota.progreso >= 1.0 and not nota.larga_completada:
                            nota.larga_completada = True
                            nota.activa = False
                            puntaje += 30
                            crear_onda(
                                nota.columna * columna_ancho + columna_ancho // 2,
                                nota.y + nota.duracion,
                                (255, 255, 255)
                            )

                
                # Verificar si pasó la zona sin ser golpeada
                elif nota.y > ZONA_GOLPEO_Y + 100:
                    nota.activa = False
                    combo = 0
                    puntaje -= 30  # Penalización por fallo
                    vidas -= 1     # Restar vida inmediatamente

                    if vidas <= 0:
                        juego_activo = False
        
        # Penalizar por presionar teclas sin motivo
        for i in range(4):
            if teclas[i]:
                # Verificar si hay alguna nota en la misma columna cerca de la zona
                nota_cercana = False
                for nota in notas:
                    if nota.columna == i and abs(nota.y - ZONA_GOLPEO_Y) < 150:
                        nota_cercana = True
                        break
                
                if not nota_cercana and ahora - ultima_penalizacion > 0.1:
                    puntaje -= 5  # Penalización por pulsación innecesaria
                    pulsaciones_innecesarias += 1
                    ultima_penalizacion = ahora
    
    dibujar()

pygame.quit()
sys.exit()