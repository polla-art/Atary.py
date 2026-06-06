# =============================================================================
# bullet.py — Classe do projétil disparado pela nave
# =============================================================================

import pygame
from settings import (
    BULLET_SPEED, BULLET_WIDTH, BULLET_HEIGHT,
    COLOR_BULLET, COLOR_ACCENT
)


class Bullet(pygame.sprite.Sprite):
    """Representa um projétil disparado pelo jogador.
    
    O projétil nasce na posição da nave e sobe em linha reta até
    acertar um asteroide ou sair pelo topo da tela.
    """

    def __init__(self, x: int, y: int):
        super().__init__()

        # --- Superfície do projétil com efeito de brilho ---
        # Cria a imagem com transparência para o efeito luminoso
        self.image = pygame.Surface((BULLET_WIDTH + 4, BULLET_HEIGHT + 4), pygame.SRCALPHA)

        # Desenha o brilho externo (halo azul ciano)
        pygame.draw.rect(
            self.image, (*COLOR_ACCENT, 60),
            (0, 0, BULLET_WIDTH + 4, BULLET_HEIGHT + 4),
            border_radius=3
        )

        # Desenha o núcleo do projétil (amarelo dourado)
        pygame.draw.rect(
            self.image, COLOR_BULLET,
            (2, 2, BULLET_WIDTH, BULLET_HEIGHT),
            border_radius=2
        )

        # --- Retângulo de colisão e posição inicial ---
        self.rect = self.image.get_rect()
        self.rect.centerx = x  # Alinha horizontalmente ao centro da nave
        self.rect.bottom = y   # Nasce na ponta superior da nave

        # Posição Y com ponto flutuante para movimento suave
        self._y = float(self.rect.y)

    def update(self):
        """Move o projétil para cima a cada frame."""
        self._y -= BULLET_SPEED
        self.rect.y = int(self._y)

        # Remove o projétil se sair pelo topo da tela
        if self.rect.bottom < 0:
            self.kill()
