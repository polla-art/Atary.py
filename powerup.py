# =============================================================================
# powerup.py — Power-up do segundo canhão (conquista da Fase 2)
# Desce pela tela após o jogador destruir POWERUP_TRIGGER meteoros
# =============================================================================

import pygame
import math
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    POWERUP_SPEED,
    COLOR_POWERUP, COLOR_POWERUP_GLOW, COLOR_ACCENT
)


class Powerup(pygame.sprite.Sprite):
    """Representa o power-up de duplo canhão que desce pela tela.

    Comportamento:
    - Aparece no topo após o jogador destruir POWERUP_TRIGGER meteoros
    - Desce em velocidade constante com animação de pulso dourado
    - Colidiu com a nave → ativa o duplo canhão e inicia a Fase 2
    - Saiu pela base da tela → desaparece sem penalidade
    """

    # Tamanho da célula pixel art e dimensões da grade
    PIXEL  = 4          # Pixels reais por "pixel" da arte
    COLS   = 11         # Colunas da grade pixel art
    ROWS   = 9          # Linhas da grade pixel art

    # Grade pixel art do ícone (1=corpo, 2=canhão/ciano, 3=propulsor/laranja, 0=vazio)
    ARTE = [
        [0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0],  # Linha 0 — pontas dos canhões
        [0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0],  # Linha 1
        [0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0],  # Linha 2 — extensão lateral
        [0, 1, 1, 1, 2, 2, 2, 1, 1, 1, 0],  # Linha 3 — asa + cockpit
        [1, 1, 1, 1, 2, 2, 2, 1, 1, 1, 1],  # Linha 4 — corpo principal
        [1, 1, 1, 1, 2, 2, 2, 1, 1, 1, 1],  # Linha 5
        [1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1],  # Linha 6 — propulsores laterais
        [0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0],  # Linha 7 — chamas
        [0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0],  # Linha 8 — chamas
    ]

    def __init__(self):
        super().__init__()

        # Dimensões totais da superfície
        self._w = self.COLS * self.PIXEL
        self._h = self.ROWS * self.PIXEL

        # Frame de animação (usado para pulso senoidal)
        self._frame = 0

        # Cria a superfície base
        self.image = self._renderizar(1.0)
        self.rect  = self.image.get_rect()

        # Posição inicial: centro horizontal no topo da tela
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.y = -self._h

        # Posição Y flutuante para movimento suave
        self._y = float(self.rect.y)

    def _renderizar(self, escala_brilho: float) -> pygame.Surface:
        """Desenha a pixel art com intensidade de brilho variável para o pulso."""
        surf = pygame.Surface((self._w + 12, self._h + 12), pygame.SRCALPHA)
        ox, oy = 6, 6  # Offset para o halo de brilho

        # --- Halo de brilho ao redor (glow) ---
        brilho_alpha = int(60 * escala_brilho)
        for dy in range(-2, self._h + 2):
            for dx in range(-2, self._w + 2):
                pass  # (o halo é feito por círculo abaixo)

        pygame.draw.ellipse(
            surf,
            (*COLOR_POWERUP_GLOW, brilho_alpha),
            (0, oy - 2, self._w + 12, self._h + 4)
        )

        # --- Pixels da arte ---
        r_body = tuple(min(255, int(c * (0.75 + 0.25 * escala_brilho))) for c in COLOR_POWERUP)
        r_cock = COLOR_ACCENT
        r_thruster = (255, min(255, int(140 * (0.6 + 0.4 * escala_brilho))), 0)

        for row, linha in enumerate(self.ARTE):
            for col, val in enumerate(linha):
                if val == 0:
                    continue
                cor = r_body if val == 1 else (r_cock if val == 2 else r_thruster)
                rect = pygame.Rect(
                    ox + col * self.PIXEL,
                    oy + row * self.PIXEL,
                    self.PIXEL,
                    self.PIXEL
                )
                pygame.draw.rect(surf, cor, rect)

        # Contorno sutil
        pygame.draw.rect(surf, (*COLOR_POWERUP, 80), (ox, oy, self._w, self._h), 1)

        return surf

    def update(self):
        """Move o power-up para baixo e anima o pulso."""
        # Descida constante
        self._y += POWERUP_SPEED
        self._frame += 1

        # Pulso senoidal: oscila entre 0.5 e 1.0
        escala = 0.5 + 0.5 * math.sin(self._frame * 0.08)

        # Recria a superfície com o brilho atual
        centro_anterior = self.rect.center
        self.image = self._renderizar(escala)
        self.rect = self.image.get_rect(center=centro_anterior)
        self.rect.y = int(self._y)

    @property
    def saiu_da_tela(self) -> bool:
        """Retorna True se o power-up ultrapassou a base da tela."""
        return self.rect.top > SCREEN_HEIGHT
