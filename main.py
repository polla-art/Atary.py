# =============================================================================
# main.py — Ponto de entrada do jogo Asteroid Blast
# Inicializa o pygame, cria a janela e dispara o loop principal
# =============================================================================

import pygame
import sys
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from game import Game


def main():
    """Função principal: configura o ambiente e inicia o jogo."""

    # --- Inicializa o pygame e todos os seus submódulos ---
    pygame.init()
    pygame.display.set_caption("Asteroid Blast  |  Atari-Style")

    # Define o ícone da janela (pequeno triângulo verde no estilo da nave)
    icone = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.polygon(icone, (57, 255, 20), [(16, 2), (2, 30), (30, 30)])
    pygame.display.set_icon(icone)

    # --- Cria a janela do jogo ---
    tela = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # --- Instancia e executa o jogo ---
    jogo = Game(tela)
    jogo.run()

    # --- Encerra o pygame ao sair do loop ---
    pygame.quit()
    sys.exit()


# Ponto de entrada padrão Python
if __name__ == "__main__":
    main()
