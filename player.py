# =============================================================================
# player.py — Nave do jogador em pixel art com suporte a duplo canhão
# =============================================================================

import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    PLAYER_SPEED, PLAYER_SHOOT_DELAY,
    COLOR_PLAYER, COLOR_PLAYER_DARK,
    COLOR_COCKPIT, COLOR_THRUSTER, COLOR_BULLET, COLOR_ACCENT
)
from bullet import Bullet


class Player(pygame.sprite.Sprite):
    """Nave espacial do jogador desenhada em pixel art.

    Controles:
      ← / →  — Move horizontalmente
      ESPAÇO — Dispara (cooldown ativo)

    Modos:
      Normal    — 1 canhão central
      Duplo     — 2 canhões laterais (ativado pelo power-up da Fase 2)
    """

    # Tamanho de cada "pixel" da arte em pixels reais
    PIXEL = 4

    # Grade pixel art da nave (modo simples — 1 canhão central)
    # Legenda: 0=vazio  1=corpo  2=cockpit  3=propulsor  4=canhão
    ARTE_SIMPLES = [
        [0, 0, 0, 0, 4, 0, 0, 0, 0],  # ponta do canhão
        [0, 0, 0, 0, 4, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 0, 0, 0],  # fuselagem superior
        [0, 0, 1, 1, 2, 1, 1, 0, 0],  # asa + cockpit
        [0, 1, 1, 1, 2, 1, 1, 1, 0],  # corpo
        [1, 1, 1, 1, 1, 1, 1, 1, 1],  # base
        [1, 0, 1, 0, 0, 0, 1, 0, 1],  # suporte propulsores
        [0, 0, 3, 0, 0, 0, 3, 0, 0],  # propulsores
        [0, 0, 3, 0, 0, 0, 3, 0, 0],  # chamas
    ]

    # Grade pixel art da nave com duplo canhão
    ARTE_DUPLO = [
        [0, 4, 0, 0, 0, 0, 0, 4, 0],  # 2 pontas de canhão
        [0, 4, 0, 0, 0, 0, 0, 4, 0],
        [0, 1, 0, 1, 1, 1, 0, 1, 0],  # fuselagem com 2 tubos
        [0, 1, 1, 1, 2, 1, 1, 1, 0],  # asa + cockpit
        [1, 1, 1, 1, 2, 1, 1, 1, 1],  # corpo
        [1, 1, 1, 1, 1, 1, 1, 1, 1],  # base
        [1, 0, 1, 0, 0, 0, 1, 0, 1],  # suporte propulsores
        [0, 0, 3, 0, 0, 0, 3, 0, 0],  # propulsores
        [0, 0, 3, 0, 0, 0, 3, 0, 0],  # chamas
    ]

    # Número de colunas e linhas da grade
    COLS = 9
    ROWS = 9

    def __init__(self):
        super().__init__()

        self.duplo_canhao = False   # Alterado ao coletar o power-up

        # Cria a superfície inicial (modo simples)
        self.image = self._criar_imagem(duplo=False)
        self.rect  = self.image.get_rect()

        # Posição: centro inferior da tela
        self.rect.centerx = SCREEN_WIDTH  // 2
        self.rect.bottom   = SCREEN_HEIGHT - 20

        # Posição X flutuante para movimento suave
        self._x = float(self.rect.x)

        # Cooldown de disparo (frames)
        self._cooldown = 0

    # -------------------------------------------------------------------------
    # Desenho da nave em pixel art
    # -------------------------------------------------------------------------

    def _criar_imagem(self, duplo: bool = False) -> pygame.Surface:
        """Desenha a nave como pixel art, com 1 ou 2 canhões."""
        arte = self.ARTE_DUPLO if duplo else self.ARTE_SIMPLES

        # Mapa de cores por valor de pixel
        cores = {
            1: COLOR_PLAYER,       # Corpo principal — verde neon
            2: COLOR_COCKPIT,      # Cockpit — azul ciano
            3: COLOR_THRUSTER,     # Propulsores — laranja
            4: (220, 255, 220),    # Canhão — branco esverdeado brilhante
        }

        # Dimensões: +2 pixels de padding de cada lado para o halo
        padding = 2
        w = self.COLS * self.PIXEL + padding * 2
        h = self.ROWS * self.PIXEL + padding * 2
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        # Halo verde suave ao redor da nave
        pygame.draw.rect(
            surf, (*COLOR_ACCENT, 20),
            (0, 0, w, h), border_radius=4
        )

        # Desenha cada pixel da arte
        for row, linha in enumerate(arte):
            for col, val in enumerate(linha):
                if val == 0:
                    continue
                cor  = cores[val]
                rect = pygame.Rect(
                    padding + col * self.PIXEL,
                    padding + row * self.PIXEL,
                    self.PIXEL,
                    self.PIXEL
                )
                pygame.draw.rect(surf, cor, rect)

                # Borda escura em cada pixel para o efeito de grade pixelada
                pygame.draw.rect(surf, COLOR_PLAYER_DARK, rect, 1)

        return surf

    # -------------------------------------------------------------------------
    # Ativação do duplo canhão
    # -------------------------------------------------------------------------

    def ativar_duplo_canhao(self):
        """Ativa o modo duplo canhão e atualiza o visual da nave."""
        self.duplo_canhao = True
        centro_atual = self.rect.center
        self.image   = self._criar_imagem(duplo=True)
        self.rect    = self.image.get_rect(center=centro_atual)

    # -------------------------------------------------------------------------
    # Atualização por frame
    # -------------------------------------------------------------------------

    def update(self, teclas: pygame.key.ScancodeWrapper,
               grupo_balas: pygame.sprite.Group):
        """Move a nave e gerencia o disparo."""

        # --- Movimento horizontal ---
        if teclas[pygame.K_LEFT]:
            self._x -= PLAYER_SPEED
        if teclas[pygame.K_RIGHT]:
            self._x += PLAYER_SPEED

        # Impede sair da tela
        self._x   = max(0, min(self._x, SCREEN_WIDTH - self.rect.width))
        self.rect.x = int(self._x)

        # --- Cooldown de disparo ---
        if self._cooldown > 0:
            self._cooldown -= 1

        # --- Disparo com ESPAÇO ---
        if teclas[pygame.K_SPACE] and self._cooldown == 0:
            topo_y = self.rect.top + 2  # Y de origem do projétil

            if self.duplo_canhao:
                # Dois projéteis: um de cada canhão lateral
                offset = self.PIXEL * 1           # Distância do centro
                bala_e = Bullet(self.rect.centerx - offset * 3, topo_y)
                bala_d = Bullet(self.rect.centerx + offset * 3, topo_y)
                grupo_balas.add(bala_e, bala_d)
            else:
                # Um projétil central
                bala = Bullet(self.rect.centerx, topo_y)
                grupo_balas.add(bala)

            self._cooldown = PLAYER_SHOOT_DELAY

    @property
    def ponta_canhao(self) -> tuple[int, int]:
        """Coordenada do canhão para referência externa."""
        return (self.rect.centerx, self.rect.top)
