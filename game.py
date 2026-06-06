# =============================================================================
# game.py — Motor central do jogo
# Orquestra o loop, spawning, colisões, pontuação e dificuldade progressiva
# =============================================================================

import pygame
import random
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    COLOR_BG, COLOR_STAR, NUM_STARS,
    ASTEROID_BASE_SPEED, ASTEROID_SPEED_INCREMENT,
    ASTEROID_SPAWN_RATE, ASTEROID_SPAWN_RATE_MIN, ASTEROID_SPAWN_REDUCE
)
from player   import Player
from bullet   import Bullet
from asteroid import Asteroid
from hud      import HUD


class Game:
    """Motor central do jogo.
    
    Gerencia:
    - O loop principal (eventos, atualização, renderização)
    - O fundo estrelado animado
    - O spawn progressivo de asteroides
    - As detecções de colisão (bala×asteroide, nave×asteroide, asteroide×fundo)
    - A pontuação e o aumento gradual de dificuldade
    - Os estados: INÍCIO, JOGANDO, GAME OVER
    """

    # Estados possíveis do jogo
    ESTADO_INICIO    = "inicio"
    ESTADO_JOGANDO   = "jogando"
    ESTADO_GAMEOVER  = "gameover"

    def __init__(self, tela: pygame.Surface):
        self.tela  = tela
        self.clock = pygame.time.Clock()
        self.hud   = HUD(tela)

        # --- Gera estrelas fixas para o fundo ---
        # Cada estrela é (x, y, raio, brilho) — brilho varia para cintilação
        self._estrelas = [
            (
                random.randint(0, SCREEN_WIDTH),
                random.randint(0, SCREEN_HEIGHT),
                random.choice([1, 1, 1, 2]),         # Raio (maioria pequeno)
                random.randint(120, 255)              # Brilho inicial
            )
            for _ in range(NUM_STARS)
        ]

        # Inicializa o estado e as variáveis do jogo
        self._reiniciar()

    # -------------------------------------------------------------------------
    # Inicialização / Reinício
    # -------------------------------------------------------------------------

    def _reiniciar(self):
        """(Re)inicializa todos os grupos de sprites e variáveis de estado."""

        # --- Grupos de sprites ---
        self.grupo_jogador   = pygame.sprite.GroupSingle()
        self.grupo_balas     = pygame.sprite.Group()
        self.grupo_asteroides = pygame.sprite.Group()

        # Cria o jogador e adiciona ao grupo
        self.jogador = Player()
        self.grupo_jogador.add(self.jogador)

        # --- Variáveis de controle ---
        self.pontuacao      = 0          # Pontuação atual
        self.estado         = self.ESTADO_INICIO
        self.frame_contador = 0          # Contador geral de frames

        # Timer de spawn (conta quantos frames faltam para o próximo asteroide)
        self._spawn_timer = 0

        # Partículas de explosão (lista de dicts com pos, vel, vida, cor)
        self._particulas = []

    # -------------------------------------------------------------------------
    # Loop principal
    # -------------------------------------------------------------------------

    def run(self):
        """Executa o loop principal do jogo até o usuário fechar a janela."""
        rodando = True
        while rodando:
            # --- Processa eventos de sistema ---
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    rodando = False
                if evento.type == pygame.KEYDOWN:
                    self._tratar_tecla(evento.key)

            # --- Atualiza a lógica conforme o estado atual ---
            if self.estado == self.ESTADO_JOGANDO:
                self._atualizar()

            # --- Renderiza o frame ---
            self._renderizar()

            # Incrementa contador de frames e mantém FPS estável
            self.frame_contador += 1
            self.clock.tick(FPS)

    # -------------------------------------------------------------------------
    # Tratamento de teclas globais
    # -------------------------------------------------------------------------

    def _tratar_tecla(self, tecla: int):
        """Trata teclas que mudam o estado do jogo."""
        if self.estado == self.ESTADO_INICIO and tecla == pygame.K_SPACE:
            # Inicia o jogo
            self.estado = self.ESTADO_JOGANDO

        elif self.estado == self.ESTADO_GAMEOVER:
            if tecla == pygame.K_r:
                # Reinicia o jogo do zero
                self._reiniciar()
                self.estado = self.ESTADO_JOGANDO
            elif tecla == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))

    # -------------------------------------------------------------------------
    # Atualização da lógica do jogo
    # -------------------------------------------------------------------------

    def _atualizar(self):
        """Atualiza todos os elementos do jogo em um frame."""

        # --- Obtém teclas pressionadas e atualiza o jogador ---
        teclas = pygame.key.get_pressed()
        self.jogador.update(teclas, self.grupo_balas)

        # --- Calcula velocidade atual dos asteroides (dificuldade progressiva) ---
        velocidade_atual = ASTEROID_BASE_SPEED + self.pontuacao * ASTEROID_SPEED_INCREMENT

        # --- Spawn de asteroides ---
        # O intervalo entre spawns diminui conforme a pontuação sobe
        intervalo_spawn = max(
            ASTEROID_SPAWN_RATE_MIN,
            int(ASTEROID_SPAWN_RATE - self.pontuacao * ASTEROID_SPAWN_REDUCE)
        )
        self._spawn_timer += 1
        if self._spawn_timer >= intervalo_spawn:
            novo = Asteroid(velocidade_atual)
            self.grupo_asteroides.add(novo)
            self._spawn_timer = 0

        # --- Atualiza projéteis e asteroides ---
        self.grupo_balas.update()
        self.grupo_asteroides.update()

        # --- Detecção de colisão: projétil × asteroide ---
        colisoes = pygame.sprite.groupcollide(
            self.grupo_balas, self.grupo_asteroides,
            True, True  # Remove ambos ao colidir
        )
        for bala, asteroides_atingidos in colisoes.items():
            for ast in asteroides_atingidos:
                self.pontuacao += 1  # Soma 1 ponto por asteroide destruído
                self._criar_explosao(ast.rect.center, ast.raio)

        # --- Detecção de colisão: nave × asteroide ---
        if pygame.sprite.spritecollide(self.jogador, self.grupo_asteroides, False,
                                        pygame.sprite.collide_circle_ratio(0.75)):
            self._criar_explosao(self.jogador.rect.center, 30)
            self.estado = self.ESTADO_GAMEOVER

        # --- Asteroide saiu pelo fundo da tela → Game Over ---
        for ast in list(self.grupo_asteroides):
            if ast.saiu_da_tela:
                self.estado = self.ESTADO_GAMEOVER
                break

        # --- Atualiza partículas de explosão ---
        self._atualizar_particulas()

    # -------------------------------------------------------------------------
    # Sistema de partículas de explosão
    # -------------------------------------------------------------------------

    def _criar_explosao(self, centro: tuple, raio: int):
        """Cria partículas de explosão no ponto de impacto."""
        num = raio * 2  # Mais partículas para asteroides maiores
        for _ in range(num):
            angulo = random.uniform(0, 360)
            speed  = random.uniform(1, raio * 0.3)
            import math
            vx = math.cos(math.radians(angulo)) * speed
            vy = math.sin(math.radians(angulo)) * speed
            cor = random.choice([
                (255, 200, 50),   # Amarelo
                (255, 120, 30),   # Laranja
                (255, 255, 255),  # Branco
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
        """Move e envelhece cada partícula; remove as que expiraram."""
        vivas = []
        for p in self._particulas:
            p["x"]    += p["vx"]
            p["y"]    += p["vy"]
            p["vy"]   += 0.15   # Gravidade leve
            p["vida"] -= 1
            if p["vida"] > 0:
                vivas.append(p)
        self._particulas = vivas

    # -------------------------------------------------------------------------
    # Renderização
    # -------------------------------------------------------------------------

    def _renderizar(self):
        """Desenha todos os elementos na tela."""

        # --- Fundo preto ---
        self.tela.fill(COLOR_BG)

        # --- Estrelas do fundo ---
        self._desenhar_estrelas()

        if self.estado == self.ESTADO_INICIO:
            # Desenha apenas o HUD de início
            self.hud.desenhar_tela_inicio(self.frame_contador)

        else:
            # --- Sprites do jogo ---
            self.grupo_asteroides.draw(self.tela)
            self.grupo_balas.draw(self.tela)
            self.grupo_jogador.draw(self.tela)

            # --- Partículas de explosão ---
            self._desenhar_particulas()

            # --- HUD: pontuação e velocidade ---
            self.hud.desenhar_hud(self.pontuacao)

            # --- Tela de Game Over (sobreposta) ---
            if self.estado == self.ESTADO_GAMEOVER:
                self.hud.desenhar_game_over(self.pontuacao, self.frame_contador)

        # Atualiza o display
        pygame.display.flip()

    def _desenhar_estrelas(self):
        """Desenha o campo de estrelas com efeito sutil de cintilação."""
        for i, (x, y, raio, brilho_base) in enumerate(self._estrelas):
            # Cintilação: oscila o brilho de forma senoidal por índice
            import math
            brilho = int(brilho_base * (0.7 + 0.3 * math.sin(self.frame_contador * 0.03 + i)))
            brilho = max(60, min(255, brilho))
            cor = (brilho, brilho, brilho + 20)  # Levemente azulado
            pygame.draw.circle(self.tela, cor, (x, y), raio)

    def _desenhar_particulas(self):
        """Desenha as partículas de explosão com fade-out."""
        for p in self._particulas:
            # Opacidade diminui conforme a vida acaba
            alpha = int(255 * (p["vida"] / 35))
            alpha = max(0, min(255, alpha))
            cor_fade = (*p["cor"][:3], alpha)
            surf = pygame.Surface((p["raio"] * 2, p["raio"] * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, cor_fade, (p["raio"], p["raio"]), p["raio"])
            self.tela.blit(surf, (int(p["x"]) - p["raio"], int(p["y"]) - p["raio"]))
