import pygame
import sys
import threading
from config import *
from game import Game
from drawing import draw_game
from serial_reader import SerialReader

def game_logic_thread(game, serial_reader, running_event):
    while running_event.is_set():
        teclas = serial_reader.get_key_states()
        game.update(teclas)
        pygame.time.Clock().tick(60)

def main():
    pygame.init()
    reloj = pygame.time.Clock()

    game = Game()
    serial_reader = SerialReader()
    serial_reader.start()

    running_event = threading.Event()
    running_event.set()

    logic_thread = threading.Thread(target=game_logic_thread, args=(game, serial_reader, running_event))
    logic_thread.start()

    corriendo = True
    while corriendo:
        reloj.tick(60)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r and not game.juego_activo:
                    game.reiniciar_juego()
                if evento.key == pygame.K_ESCAPE:
                    corriendo = False

        # The drawing needs the key states for visual feedback
        teclas = serial_reader.get_key_states()
        draw_game(game, teclas)

    running_event.clear()
    logic_thread.join()
    serial_reader.stop()
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
