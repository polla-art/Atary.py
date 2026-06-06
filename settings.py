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

# --- Paleta de cores (estilo retrô neon) ---
COLOR_BG         = (0,   0,   0)    # Preto — fundo da tela
COLOR_PLAYER     = (57,  255, 20)   # Verde neon — nave do jogador
COLOR_BULLET     = (255, 215, 0)    # Amarelo ouro — projéteis
COLOR_ASTEROID   = (210, 105, 30)   # Laranja queimado — asteroides
COLOR_ASTEROID2  = (160, 82,  45)   # Marrom avermelhado — detalhes dos asteroides
COLOR_HUD        = (255, 255, 255)  # Branco — textos do HUD
COLOR_GAMEOVER   = (255, 50,  50)   # Vermelho — tela de game over
COLOR_TITLE      = (57,  255, 20)   # Verde neon — título do jogo
COLOR_ACCENT     = (0,   200, 255)  # Azul ciano — destaques e bordas
COLOR_STAR       = (180, 180, 200)  # Cinza azulado — estrelas do fundo

# --- Estrelas do fundo ---
NUM_STARS = 80  # Quantidade de estrelas decorativas no fundo
