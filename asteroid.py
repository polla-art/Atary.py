# =============================================================================
# asteroid.py — Classe do asteroide
# =============================================================================

import pygame
import random
import math
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_ASTEROID, COLOR_ASTEROID2
)


class Asteroid(pygame.sprite.Sprite):
    """Representa um asteroide que cai do topo para o fundo da tela.
    
    Cada asteroide tem:
    - Tamanho aleatório (pequeno, médio ou grande)
    - Forma poligonal irregular para visual retrô
    - Rotação suave enquanto cai
    - Velocidade fornecida pelo Game (aumenta com a pontuação)
    """

    # Raios possíveis para cada categoria de tamanho
    TAMANHOS = {
        'pequeno': (14, 20),
        'medio':   (22, 30),
        'grande':  (32, 42),
    }

    def __init__(self, velocidade: float):
        super().__init__()

        # --- Escolhe tamanho e raio aleatório ---
        categoria = random.choice(list(self.TAMANHOS.keys()))
        raio_min, raio_max = self.TAMANHOS[categoria]
        self.raio = random.randint(raio_min, raio_max)

        # --- Velocidade de queda (controlada pelo Game) ---
        self.velocidade = velocidade

        # --- Velocidade de rotação aleatória ---
        self.angulo = 0.0
        self.vel_rotacao = random.uniform(-2.5, 2.5)

        # --- Gera o polígono irregular do asteroide ---
        # Cria N vértices distribuídos em torno de um círculo com variação de raio
        num_vertices = random.randint(7, 11)
        self._pontos_base = []
        for i in range(num_vertices):
            angulo_v = (2 * math.pi / num_vertices) * i
            variacao = random.uniform(0.6, 1.0)  # Irregularidade da forma
            r = self.raio * variacao
            px = r * math.cos(angulo_v)
            py = r * math.sin(angulo_v)
            self._pontos_base.append((px, py))

        # --- Cria a superfície inicial ---
        tam = self.raio * 2 + 4  # Espaço extra para não cortar as bordas
        self.image = self._renderizar(self.angulo, tam)
        self.rect  = self.image.get_rect()

        # --- Posição inicial: aleatória no topo, escondida um pouco acima ---
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = -self.rect.height

        # Posição Y com ponto flutuante para movimento suave
        self._y = float(self.rect.y)

    def _renderizar(self, angulo: float, tam: int) -> pygame.Surface:
        """Cria (ou recria) a superfície com o asteroide rotacionado."""
        surf = pygame.Surface((tam, tam), pygame.SRCALPHA)
        centro = (tam // 2, tam // 2)

        # Rotaciona os pontos base pelo ângulo atual
        rad = math.radians(angulo)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        pontos_rot = []
        for px, py in self._pontos_base:
            rx = px * cos_a - py * sin_a + centro[0]
            ry = px * sin_a + py * cos_a + centro[1]
            pontos_rot.append((rx, ry))

        # Desenha o preenchimento do asteroide
        pygame.draw.polygon(surf, COLOR_ASTEROID, pontos_rot)

        # Desenha a borda escura para dar profundidade
        pygame.draw.polygon(surf, COLOR_ASTEROID2, pontos_rot, 2)

        # Adiciona alguns "pontos de cratera" para detalhe visual
        random.seed(id(self))  # Usa ID fixo para que os detalhes não mudem
        for _ in range(3):
            cx = random.randint(centro[0] - self.raio // 2, centro[0] + self.raio // 2)
            cy = random.randint(centro[1] - self.raio // 2, centro[1] + self.raio // 2)
            cr = random.randint(2, max(3, self.raio // 5))
            pygame.draw.circle(surf, COLOR_ASTEROID2, (cx, cy), cr)
        random.seed()  # Restaura seed aleatória

        return surf

    def update(self):
        """Move o asteroide para baixo e aplica rotação a cada frame."""
        # Desce o asteroide
        self._y += self.velocidade
        self.rect.y = int(self._y)

        # Atualiza rotação
        self.angulo = (self.angulo + self.vel_rotacao) % 360
        tam = self.raio * 2 + 4
        pos_centro = self.rect.center  # Preserva o centro ao recriar a superfície
        self.image = self._renderizar(self.angulo, tam)
        self.rect  = self.image.get_rect(center=pos_centro)
        self.rect.y = int(self._y)

    @property
    def saiu_da_tela(self) -> bool:
        """Retorna True se o asteroide cruzou o fundo da tela."""
        return self.rect.top > SCREEN_HEIGHT
