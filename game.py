# =============================================================================
# game.py — Motor central do jogo (Fase 1 e Fase 2)
# =============================================================================

import pygame
import random
import math
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    COLOR_BG, COLOR_STAR, NUM_STARS,
    ASTEROID_BASE_SPEED, ASTEROID_SPEED_INCREMENT,
    ASTEROID_SPAWN_RATE, ASTEROID_SPAWN_RATE_MIN, ASTEROID_SPAWN_REDUCE,
    POWERUP_TRIGGER, FASE2_SPEED_BONUS
)
from player   import Player
from bullet   import Bullet
from asteroid import Asteroid
from powerup  import Powerup
from hud      import HUD


class Game:
    """Motor central do jogo.

    Gerencia:
    - Loop principal (eventos, atualização, renderização)
    - Fundo estrelado animado
    - Spawn de asteroides com dificuldade progressiva
    - Detecção de colisões (bala×asteroide, nave×asteroide, nave×powerup)
    - Sistema de fases: Fase 1 → Power-up → Fase 2
    - Pontuação e estados do jogo
    """

    ESTADO_INICIO   = "inicio"
    ESTADO_JOGANDO  = "jogando"
    ESTADO_GAMEOVER = "gameover"

    def __init__(self, tela: pygame.Surface):
        self.tela  = tela
        self.clock = pygame.time.Clock()
        self.hud   = HUD(tela)

        # --- Campo de estrelas fixo (gerado uma vez) ---
        self._estrelas = [
            (
                random.randint(0, SCREEN_WIDTH),
                random.randint(0, SCREEN_HEIGHT),
                random.choice([1, 1, 1, 2]),
                random.randint(120, 255)
            )
            for _ in range(NUM_STARS)
        ]

        self._reiniciar()

    # -------------------------------------------------------------------------
    # Inicialização / Reinício
    # -------------------------------------------------------------------------

    def _reiniciar(self):
        """Reinicia todos os grupos de sprites e variáveis de estado."""

        # Grupos de sprites
        self.grupo_jogador    = pygame.sprite.GroupSingle()
        self.grupo_balas      = pygame.sprite.Group()
        self.grupo_asteroides = pygame.sprite.Group()
        self.grupo_powerups   = pygame.sprite.Group()

        # Cria e posiciona o jogador
        self.jogador = Player()
        self.grupo_jogador.add(self.jogador)

        # Variáveis de controle
        self.pontuacao      = 0
        self.estado         = self.ESTADO_INICIO
        self.frame_contador = 0
        self.fase           = 1                  # Fase atual (1 ou 2)
        self._powerup_gerado = False             # Garante apenas 1 power-up por partida
        self._banner_timer   = 0                 # Frames restantes do banner de transição
        self._spawn_timer    = 0

        # Partículas de explosão
        self._particulas = []

    # -------------------------------------------------------------------------
    # Loop principal
    # -------------------------------------------------------------------------

    def run(self):
        """Executa o loop principal até o jogador fechar a janela."""
        rodando = True
        while rodando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    rodando = False
                if evento.type == pygame.KEYDOWN:
                    self._tratar_tecla(evento.key)

            if self.estado == self.ESTADO_JOGANDO:
                self._atualizar()

            self._renderizar()
            self.frame_contador += 1
            self.clock.tick(FPS)

    # -------------------------------------------------------------------------
    # Teclas de estado
    # -------------------------------------------------------------------------

    def _tratar_tecla(self, tecla: int):
        """Trata transições de estado via teclado."""
        if self.estado == self.ESTADO_INICIO and tecla == pygame.K_SPACE:
            self.estado = self.ESTADO_JOGANDO

        elif self.estado == self.ESTADO_GAMEOVER:
            if tecla == pygame.K_r:
                self._reiniciar()
                self.estado = self.ESTADO_JOGANDO
            elif tecla == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))

    # -------------------------------------------------------------------------
    # Atualização da lógica
    # -------------------------------------------------------------------------

    def _atualizar(self):
        """Atualiza todos os elementos do jogo em um frame."""

        # --- Jogador ---
        teclas = pygame.key.get_pressed()
        self.jogador.update(teclas, self.grupo_balas)

        # --- Velocidade atual dos asteroides (Fase 1 ou 2) ---
        bonus_fase = FASE2_SPEED_BONUS if self.fase == 2 else 0.0
        velocidade_atual = (ASTEROID_BASE_SPEED + bonus_fase
                            + self.pontuacao * ASTEROID_SPEED_INCREMENT)

        # --- Spawn de asteroides ---
        intervalo_spawn = max(
            ASTEROID_SPAWN_RATE_MIN,
            int(ASTEROID_SPAWN_RATE - self.pontuacao * ASTEROID_SPAWN_REDUCE)
        )
        self._spawn_timer += 1
        if self._spawn_timer >= intervalo_spawn:
            novo = Asteroid(velocidade_atual, fase=self.fase)
            self.grupo_asteroides.add(novo)
            self._spawn_timer = 0

        # --- Spawn do power-up (só uma vez, ao atingir POWERUP_TRIGGER pontos) ---
        if (not self._powerup_gerado and self.fase == 1
                and self.pontuacao >= POWERUP_TRIGGER):
            pu = Powerup()
            self.grupo_powerups.add(pu)
            self._powerup_gerado = True

        # --- Atualiza sprites ---
        self.grupo_balas.update()
        self.grupo_asteroides.update()
        self.grupo_powerups.update()

        # --- Colisão: projétil × asteroide ---
        # Não remove o asteroide diretamente — chama receber_dano()
        colisoes = pygame.sprite.groupcollide(
            self.grupo_balas, self.grupo_asteroides,
            True, False   # Remove a bala, mas NÃO o asteroide ainda
        )
        for _bala, asteroides_atingidos in colisoes.items():
            for ast in asteroides_atingidos:
                destruido = ast.receber_dano()
                if destruido:
                    self.pontuacao += 1
                    self._criar_explosao(ast.rect.center, ast.raio)
                    ast.kill()   # Remove o asteroide destruído

        # --- Colisão: nave × power-up ---
        coletados = pygame.sprite.spritecollide(
            self.jogador, self.grupo_powerups, True
        )
        if coletados:
            self._ativar_fase2()

        # --- Remove power-ups que saíram da tela ---
        for pu in list(self.grupo_powerups):
            if pu.saiu_da_tela:
                pu.kill()

        # --- Colisão: nave × asteroide → Game Over ---
        if pygame.sprite.spritecollide(
            self.jogador, self.grupo_asteroides, False,
            pygame.sprite.collide_circle_ratio(0.75)
        ):
            self._criar_explosao(self.jogador.rect.center, 30)
            self.estado = self.ESTADO_GAMEOVER

        # --- Asteroide saiu pelo fundo → Game Over ---
        for ast in list(self.grupo_asteroides):
            if ast.saiu_da_tela:
                self.estado = self.ESTADO_GAMEOVER
                break

        # --- Atualiza partículas e banner ---
        self._atualizar_particulas()
        if self._banner_timer > 0:
            self._banner_timer -= 1

    # -------------------------------------------------------------------------
    # Ativação da Fase 2
    # -------------------------------------------------------------------------

    def _ativar_fase2(self):
        """Ativa a Fase 2: duplo canhão na nave e asteroides mais resistentes."""
        self.fase = 2
        self.jogador.ativar_duplo_canhao()
        self._banner_timer = 180   # Banner visível por 3 segundos (180 frames)

    # -------------------------------------------------------------------------
    # Partículas de explosão
    # -------------------------------------------------------------------------

    def _criar_explosao(self, centro: tuple, raio: int):
        """Gera partículas de explosão no ponto de impacto."""
        num = raio * 2
        for _ in range(num):
            angulo = random.uniform(0, 360)
            speed  = random.uniform(1, raio * 0.3)
            vx = math.cos(math.radians(angulo)) * speed
            vy = math.sin(math.radians(angulo)) * speed
            cor = random.choice([
                (255, 200, 50),
                (255, 120, 30),
                (255, 255, 255),
            ])
            self._particulas.append({
                "x":    float(centro[0]),
                "y":    float(centro[1]),
                "vx":   vx,
                "vy":   vy,
                "vida": random.randint(15, 35),
                "cor":  cor,
                "raio": random.randint(1, 3),
            })

    def _atualizar_particulas(self):
        """Move e envelhece as partículas; remove as expiradas."""
        vivas = []
        for p in self._particulas:
            p["x"]    += p["vx"]
            p["y"]    += p["vy"]
            p["vy"]   += 0.15
            p["vida"] -= 1
            if p["vida"] > 0:
                vivas.append(p)
        self._particulas = vivas

    # -------------------------------------------------------------------------
    # Renderização
    # -------------------------------------------------------------------------

    def _renderizar(self):
        """Desenha todos os elementos na tela a cada frame."""
        self.tela.fill(COLOR_BG)
        self._desenhar_estrelas()

        if self.estado == self.ESTADO_INICIO:
            self.hud.desenhar_tela_inicio(self.frame_contador)

        else:
            # Sprites
            self.grupo_asteroides.draw(self.tela)
            self.grupo_powerups.draw(self.tela)
            self.grupo_balas.draw(self.tela)
            self.grupo_jogador.draw(self.tela)

            # Partículas
            self._desenhar_particulas()

            # HUD (com estado de fase e banner)
            self.hud.desenhar_hud(
                self.pontuacao,
                fase=self.fase,
                duplo_canhao=self.jogador.duplo_canhao,
                banner_timer=self._banner_timer
            )

            # Game Over
            if self.estado == self.ESTADO_GAMEOVER:
                self.hud.desenhar_game_over(
                    self.pontuacao,
                    self.frame_contador,
                    fase=self.fase
                )

        pygame.display.flip()

    def _desenhar_estrelas(self):
        """Campo de estrelas com cintilação senoidal."""
        for i, (x, y, raio, brilho_base) in enumerate(self._estrelas):
            brilho = int(brilho_base * (0.7 + 0.3 * math.sin(
                self.frame_contador * 0.03 + i)))
            brilho = max(60, min(255, brilho))
            cor    = (brilho, brilho, min(255, brilho + 20))
            pygame.draw.circle(self.tela, cor, (x, y), raio)

    def _desenhar_particulas(self):
        """Partículas de explosão com fade-out por alpha."""
        for p in self._particulas:
            alpha    = max(0, min(255, int(255 * p["vida"] / 35)))
            cor_fade = (*p["cor"][:3], alpha)
            surf     = pygame.Surface((p["raio"] * 2, p["raio"] * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, cor_fade, (p["raio"], p["raio"]), p["raio"])
            self.tela.blit(surf, (int(p["x"]) - p["raio"], int(p["y"]) - p["raio"]))
