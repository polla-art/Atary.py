# =============================================================================
# settings.py — Configurações globais do jogo
# Todas as constantes ficam aqui para facilitar ajustes sem mexer em outros arquivos
# =============================================================================

# --- Tela ---
SCREEN_WIDTH  = 800   # Largura da janela em pixels
SCREEN_HEIGHT = 600   # Altura da janela em pixels
FPS           = 60    # Quadros por segundo

# --- Jogador ---
PLAYER_SPEED      = 6    # Velocidade horizontal da nave (pixels por frame)
PLAYER_SHOOT_DELAY = 20  # Cooldown de disparo em frames (evita spam de tiros)

# --- Projéteis ---
BULLET_SPEED  = 12   # Velocidade do projétil subindo (pixels por frame)
BULLET_WIDTH  = 4    # Largura do projétil em pixels
BULLET_HEIGHT = 14   # Altura do projétil em pixels

# --- Asteroides ---
ASTEROID_BASE_SPEED      = 2.0    # Velocidade inicial dos asteroides (pixels/frame)
ASTEROID_SPEED_INCREMENT = 0.04   # Aumento de velocidade a cada ponto ganho
ASTEROID_SPAWN_RATE      = 60     # Intervalo inicial entre spawns (em frames)
ASTEROID_SPAWN_RATE_MIN  = 20     # Intervalo mínimo entre spawns (jogo no limite)
ASTEROID_SPAWN_REDUCE    = 0.5    # Redução no intervalo por ponto ganho

# --- Sistema de Fases ---
POWERUP_TRIGGER      = 10   # Meteoros necessários para spawnar o power-up
POWERUP_SPEED        = 1.5  # Velocidade de queda do power-up (pixels/frame)
FASE2_ASTEROID_HP    = 2    # Pontos de vida dos asteroides na fase 2
FASE2_SPEED_BONUS    = 1.0  # Bônus de velocidade base na fase 2

# --- Paleta de cores (estilo retrô neon) ---
COLOR_BG            = (0,   0,   0)    # Preto — fundo da tela
COLOR_PLAYER        = (57,  255, 20)   # Verde neon — nave do jogador
COLOR_PLAYER_DARK   = (20,  140, 8)    # Verde escuro — detalhes da nave
COLOR_COCKPIT       = (0,   200, 255)  # Ciano — cockpit da nave
COLOR_THRUSTER      = (255, 140, 0)    # Laranja — propulsores
COLOR_BULLET        = (255, 215, 0)    # Amarelo ouro — projéteis
COLOR_ASTEROID      = (210, 105, 30)   # Laranja queimado — asteroides fase 1
COLOR_ASTEROID2     = (160, 82,  45)   # Marrom avermelhado — detalhes fase 1
COLOR_ASTEROID_F2   = (70,  110, 180)  # Azul aço — asteroides fase 2
COLOR_ASTEROID_F2B  = (0,   200, 255)  # Ciano — borda asteroides fase 2
COLOR_POWERUP       = (255, 215, 0)    # Dourado — power-up
COLOR_POWERUP_GLOW  = (255, 165, 0)    # Laranja dourado — brilho do power-up
COLOR_HUD           = (255, 255, 255)  # Branco — textos do HUD
COLOR_GAMEOVER      = (255, 50,  50)   # Vermelho — tela de game over
COLOR_TITLE         = (57,  255, 20)   # Verde neon — título do jogo
COLOR_ACCENT        = (0,   200, 255)  # Azul ciano — destaques e bordas
COLOR_FASE2         = (0,   200, 255)  # Ciano — indicador fase 2
COLOR_STAR          = (180, 180, 200)  # Cinza azulado — estrelas do fundo

# --- Estrelas do fundo ---
NUM_STARS = 80  # Quantidade de estrelas decorativas no fundo
