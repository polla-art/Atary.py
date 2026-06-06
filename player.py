# =============================================================================
# player.py — Classe da nave controlada pelo jogador
# =============================================================================

import pygame
import math
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    PLAYER_SPEED, PLAYER_SHOOT_DELAY,
    COLOR_PLAYER, COLOR_ACCENT, COLOR_BULLET
)
from bullet import Bullet


class Player(pygame.sprite.Sprite):
    """Representa a nave espacial controlada pelo jogador.
    
    Controles:
      ← / →  — Move a nave horizontalmente
      ESPAÇO — Dispara um projétil (com cooldown)
    
    A nave é desenhada como um triângulo estilizado no estilo Atari,
    com efeito de brilho ao redor do contorno.
    """

    # Tamanho da nave em pixels
    LARGURA  = 46
    ALTURA   = 36

    def __init__(self):
        super().__init__()

        # --- Cria a superfície da nave ---
        self.image = self._criar_imagem()
        self.rect  = self.image.get_rect()

        # Posiciona a nave no centro inferior da tela
        self.rect.centerx = SCREEN_WIDTH  // 2
        self.rect.bottom   = SCREEN_HEIGHT - 20

        # Posição X com ponto flutuante para movimento suave
        self._x = float(self.rect.x)

        # --- Cooldown de disparo ---
        # Conta quantos frames faltam para poder disparar novamente
        self._cooldown = 0

        # --- Animação de propulsor ---
        self._frame_propulsor = 0

    def _criar_imagem(self) -> pygame.Surface:
        """Desenha a nave como um triângulo estilizado com brilho neon."""
        # Superfície extra maior para acomodar o halo de brilho
        padding = 8
        w = self.LARGURA  + padding * 2
        h = self.ALTURA   + padding * 2
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        # Pontos do triângulo principal (ponta no topo, base embaixo)
        topo   = (w // 2,          padding)
        base_e = (padding,         h - padding)
        base_d = (w - padding,     h - padding)
        asa_e  = (padding + 6,     h - padding - 8)
        asa_d  = (w - padding - 6, h - padding - 8)

        # Sombra/halo externo (verde semi-transparente)
        halo_pts = [
            (topo[0],     topo[1]   - 4),
            (base_e[0] - 4, base_e[1] + 4),
            (base_d[0] + 4, base_d[1] + 4),
        ]
        pygame.draw.polygon(surf, (*COLOR_ACCENT, 40), halo_pts)

        # Corpo principal da nave (verde neon)
        corpo_pts = [topo, asa_e, base_e, base_d, asa_d]
        pygame.draw.polygon(surf, COLOR_PLAYER, corpo_pts)

        # Contorno brilhante
        pygame.draw.polygon(surf, COLOR_ACCENT, corpo_pts, 2)

        # Detalhe central: linha da cabine
        mid_y = (topo[1] + base_e[1]) // 2
        pygame.draw.line(surf, COLOR_ACCENT,
                         (w // 2, topo[1] + 6),
                         (w // 2, mid_y - 4), 2)

        # Janela/cockpit (pequeno círculo)
        pygame.draw.circle(surf, COLOR_ACCENT,
                           (w // 2, topo[1] + 10), 4)
        pygame.draw.circle(surf, (*COLOR_BULLET, 180),
                           (w // 2, topo[1] + 10), 2)

        return surf

    def update(self, teclas_pressionadas: pygame.key.ScancodeWrapper,
               grupo_balas: pygame.sprite.Group):
        """Atualiza a posição da nave e verifica disparo.
        
        Args:
            teclas_pressionadas: Estado atual do teclado.
            grupo_balas: Grupo onde os novos projéteis serão adicionados.
        """
        # --- Movimento horizontal ---
        if teclas_pressionadas[pygame.K_LEFT]:
            self._x -= PLAYER_SPEED
        if teclas_pressionadas[pygame.K_RIGHT]:
            self._x += PLAYER_SPEED

        # Limita a nave dentro das bordas da tela
        self._x = max(0, min(self._x, SCREEN_WIDTH - self.rect.width))
        self.rect.x = int(self._x)

        # --- Cooldown de disparo ---
        if self._cooldown > 0:
            self._cooldown -= 1

        # --- Disparo com barra de espaço ---
        if teclas_pressionadas[pygame.K_SPACE] and self._cooldown == 0:
            bala = Bullet(self.rect.centerx, self.rect.top + 8)
            grupo_balas.add(bala)
            self._cooldown = PLAYER_SHOOT_DELAY  # Reinicia o cooldown

    @property
    def ponta_canhao(self) -> tuple[int, int]:
        """Retorna a coordenada do topo (ponta) da nave para o spawn das balas."""
        return (self.rect.centerx, self.rect.top)
