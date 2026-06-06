# =============================================================================
# hud.py — Interface visual do jogo (HUD, telas de início e game over)
# =============================================================================

import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_HUD, COLOR_GAMEOVER, COLOR_TITLE,
    COLOR_ACCENT, COLOR_BG, COLOR_PLAYER,
    ASTEROID_BASE_SPEED, ASTEROID_SPEED_INCREMENT
)


class HUD:
    """Gerencia toda a interface visual exibida sobre o jogo.
    
    Responsabilidades:
    - Exibir pontuação atual no canto superior esquerdo
    - Exibir indicador de velocidade/dificuldade
    - Exibir tela de início (antes do jogo começar)
    - Exibir tela de Game Over com pontuação final
    """

    def __init__(self, tela: pygame.Surface):
        self.tela = tela

        # --- Carrega fontes ---
        # Tenta usar uma fonte monoespaçada/arcade; fallback para a padrão
        try:
            self.fonte_grande  = pygame.font.SysFont("Courier New", 52, bold=True)
            self.fonte_media   = pygame.font.SysFont("Courier New", 28, bold=True)
            self.fonte_pequena = pygame.font.SysFont("Courier New", 20)
        except Exception:
            self.fonte_grande  = pygame.font.Font(None, 60)
            self.fonte_media   = pygame.font.Font(None, 36)
            self.fonte_pequena = pygame.font.Font(None, 24)

    # -------------------------------------------------------------------------
    # Tela de jogo ativo
    # -------------------------------------------------------------------------

    def desenhar_hud(self, pontuacao: int):
        """Desenha a pontuação e o indicador de velocidade durante o jogo."""

        # --- Pontuação no canto superior esquerdo ---
        texto_pts = self.fonte_media.render(f"SCORE  {pontuacao:05d}", True, COLOR_HUD)
        self.tela.blit(texto_pts, (16, 12))

        # --- Indicador de velocidade atual ---
        velocidade_atual = ASTEROID_BASE_SPEED + pontuacao * ASTEROID_SPEED_INCREMENT
        nivel = min(int((velocidade_atual - ASTEROID_BASE_SPEED) / 0.5) + 1, 10)
        texto_vel = self.fonte_pequena.render(f"SPEED  LVL {nivel}", True, COLOR_ACCENT)
        self.tela.blit(texto_vel, (16, 46))

        # --- Barra de velocidade (visual) ---
        self._desenhar_barra_velocidade(nivel, x=16, y=70)

    def _desenhar_barra_velocidade(self, nivel: int, x: int, y: int):
        """Desenha uma barra segmentada indicando o nível de dificuldade."""
        largura_seg = 14
        altura_seg  = 6
        gap         = 3
        max_segs    = 10

        for i in range(max_segs):
            cor = COLOR_ACCENT if i < nivel else (30, 60, 80)
            rect = pygame.Rect(x + i * (largura_seg + gap), y, largura_seg, altura_seg)
            pygame.draw.rect(self.tela, cor, rect, border_radius=2)

    # -------------------------------------------------------------------------
    # Tela de início
    # -------------------------------------------------------------------------

    def desenhar_tela_inicio(self, frame: int):
        """Desenha a tela de boas-vindas com animação de piscar no texto."""

        # --- Título principal ---
        titulo = self.fonte_grande.render("ASTEROID BLAST", True, COLOR_TITLE)
        self.tela.blit(titulo, titulo.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80)))

        # Linha decorativa abaixo do título
        largura_linha = titulo.get_width()
        cx = SCREEN_WIDTH // 2
        pygame.draw.line(
            self.tela, COLOR_ACCENT,
            (cx - largura_linha // 2, SCREEN_HEIGHT // 2 - 48),
            (cx + largura_linha // 2, SCREEN_HEIGHT // 2 - 48),
            2
        )

        # --- Instruções ---
        instrucoes = [
            ("← →  MOVER NAVE",      COLOR_HUD),
            ("ESPAÇO  DISPARAR",      COLOR_HUD),
            ("",                      COLOR_HUD),
        ]
        for i, (linha, cor) in enumerate(instrucoes):
            surf = self.fonte_pequena.render(linha, True, cor)
            self.tela.blit(surf, surf.get_rect(center=(SCREEN_WIDTH // 2,
                                                        SCREEN_HEIGHT // 2 + i * 30)))

        # --- "PRESS SPACE" piscando (a cada 40 frames alterna visibilidade) ---
        if (frame // 40) % 2 == 0:
            press = self.fonte_media.render("PRESSIONE ESPAÇO PARA INICIAR", True, COLOR_PLAYER)
            self.tela.blit(press, press.get_rect(center=(SCREEN_WIDTH // 2,
                                                          SCREEN_HEIGHT // 2 + 130)))

    # -------------------------------------------------------------------------
    # Tela de Game Over
    # -------------------------------------------------------------------------

    def desenhar_game_over(self, pontuacao: int, frame: int):
        """Desenha a tela de Game Over com pontuação final e opção de reiniciar."""

        # --- Overlay semi-transparente ---
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.tela.blit(overlay, (0, 0))

        # --- Texto GAME OVER ---
        go_surf = self.fonte_grande.render("GAME  OVER", True, COLOR_GAMEOVER)
        self.tela.blit(go_surf, go_surf.get_rect(center=(SCREEN_WIDTH // 2,
                                                           SCREEN_HEIGHT // 2 - 80)))

        # --- Pontuação final ---
        pts_surf = self.fonte_media.render(f"PONTUAÇÃO FINAL:  {pontuacao:05d}", True, COLOR_HUD)
        self.tela.blit(pts_surf, pts_surf.get_rect(center=(SCREEN_WIDTH // 2,
                                                             SCREEN_HEIGHT // 2)))

        # --- Opções de reinício (piscando) ---
        if (frame // 40) % 2 == 0:
            r_surf = self.fonte_media.render("R — JOGAR NOVAMENTE   ESC — SAIR", True, COLOR_ACCENT)
            self.tela.blit(r_surf, r_surf.get_rect(center=(SCREEN_WIDTH // 2,
                                                             SCREEN_HEIGHT // 2 + 70)))
