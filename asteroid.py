# =============================================================================
# asteroid.py — Classe do asteroide (Fase 1 e Fase 2)
# =============================================================================

import pygame
import random
import math
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_ASTEROID, COLOR_ASTEROID2,
    COLOR_ASTEROID_F2, COLOR_ASTEROID_F2B,
    FASE2_ASTEROID_HP
)


class Asteroid(pygame.sprite.Sprite):
    """Representa um asteroide que cai do topo para o fundo da tela.

    Na Fase 1: 1 HP, cor laranja queimado.
    Na Fase 2: 2 HP, cor azul aço, pisca branco ao ser atingido.
    """

    # Raios possíveis para cada categoria de tamanho
    TAMANHOS = {
        'pequeno': (14, 20),
        'medio':   (22, 30),
        'grande':  (32, 42),
    }

    def __init__(self, velocidade: float, fase: int = 1):
        super().__init__()

        # --- Fase e cores ---
        self.fase = fase
        if fase == 2:
            # Fase 2: asteroides mais resistentes com visual azul
            self._cor_fill  = COLOR_ASTEROID_F2
            self._cor_borda = COLOR_ASTEROID_F2B
            self.hp         = FASE2_ASTEROID_HP
        else:
            # Fase 1: asteroides clássicos laranjas
            self._cor_fill  = COLOR_ASTEROID
            self._cor_borda = COLOR_ASTEROID2
            self.hp         = 1

        # --- Tamanho e raio aleatório ---
        categoria = random.choice(list(self.TAMANHOS.keys()))
        raio_min, raio_max = self.TAMANHOS[categoria]
        self.raio = random.randint(raio_min, raio_max)

        # --- Velocidade de queda ---
        self.velocidade = velocidade

        # --- Velocidade de rotação aleatória ---
        self.angulo     = 0.0
        self.vel_rotacao = random.uniform(-2.5, 2.5)

        # --- Timer de flash branco ao receber dano (fase 2) ---
        self._flash_timer = 0  # Frames restantes de flash

        # --- Gera o polígono irregular do asteroide ---
        num_vertices = random.randint(7, 11)
        self._pontos_base = []
        for i in range(num_vertices):
            angulo_v = (2 * math.pi / num_vertices) * i
            variacao = random.uniform(0.6, 1.0)
            r  = self.raio * variacao
            px = r * math.cos(angulo_v)
            py = r * math.sin(angulo_v)
            self._pontos_base.append((px, py))

        # --- Cria a superfície inicial ---
        tam        = self.raio * 2 + 4
        self.image = self._renderizar(self.angulo, tam)
        self.rect  = self.image.get_rect()

        # --- Posição inicial no topo ---
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = -self.rect.height
        self._y     = float(self.rect.y)

    def _renderizar(self, angulo: float, tam: int, flash: bool = False) -> pygame.Surface:
        """Cria a superfície do asteroide com rotação e efeito de flash opcional."""
        surf   = pygame.Surface((tam, tam), pygame.SRCALPHA)
        centro = (tam // 2, tam // 2)

        # Rotaciona os pontos pelo ângulo atual
        rad   = math.radians(angulo)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        pontos_rot = []
        for px, py in self._pontos_base:
            rx = px * cos_a - py * sin_a + centro[0]
            ry = px * sin_a + py * cos_a + centro[1]
            pontos_rot.append((rx, ry))

        # Se flash ativo: usa branco em vez da cor normal
        cor_fill  = (240, 240, 255) if flash else self._cor_fill
        cor_borda = (255, 255, 255) if flash else self._cor_borda

        # Desenha o polígono preenchido e a borda
        pygame.draw.polygon(surf, cor_fill,  pontos_rot)
        pygame.draw.polygon(surf, cor_borda, pontos_rot, 2)

        # Crateras decorativas (semente fixa para consistência visual)
        random.seed(id(self))
        for _ in range(3):
            cx = random.randint(centro[0] - self.raio // 2, centro[0] + self.raio // 2)
            cy = random.randint(centro[1] - self.raio // 2, centro[1] + self.raio // 2)
            cr = random.randint(2, max(3, self.raio // 5))
            pygame.draw.circle(surf, cor_borda, (cx, cy), cr)
        random.seed()

        return surf

    def receber_dano(self) -> bool:
        """Aplica 1 ponto de dano ao asteroide.

        Returns:
            True  — asteroide foi destruído (HP chegou a 0)
            False — asteroide sobreviveu (ainda tem HP)
        """
        self.hp -= 1
        if self.hp <= 0:
            return True   # Destruído

        # Sobreviveu: inicia flash branco de 4 frames
        self._flash_timer = 4
        return False

    def update(self):
        """Move o asteroide para baixo, aplica rotação e gerencia flash."""
        # Descida
        self._y      += self.velocidade
        self.rect.y   = int(self._y)

        # Rotação
        self.angulo = (self.angulo + self.vel_rotacao) % 360

        # Atualiza flash
        flash = self._flash_timer > 0
        if flash:
            self._flash_timer -= 1

        # Recria a superfície com rotação e flash
        tam          = self.raio * 2 + 4
        pos_centro   = self.rect.center
        self.image   = self._renderizar(self.angulo, tam, flash=flash)
        self.rect    = self.image.get_rect(center=pos_centro)
        self.rect.y  = int(self._y)

    @property
    def saiu_da_tela(self) -> bool:
        """Retorna True se o asteroide ultrapassou o fundo da tela."""
        return self.rect.top > SCREEN_HEIGHT
