# =============================================================================
# hud.py — Interface visual do jogo (HUD, telas de início e game over)
# =============================================================================

import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_HUD, COLOR_GAMEOVER, COLOR_TITLE,
    COLOR_ACCENT, COLOR_BG, COLOR_PLAYER,
    COLOR_FASE2, COLOR_POWERUP,
    ASTEROID_BASE_SPEED, ASTEROID_SPEED_INCREMENT
)


class HUD:
    """Gerencia toda a interface visual exibida sobre o jogo.

    Responsabilidades:
    - Pontuação e nível de dificuldade durante o jogo
    - Indicador de Fase 2 e duplo canhão
    - Banner de transição ao ativar o duplo canhão
    - Tela de início com animação de piscar
    - Tela de Game Over com pontuação final
    """

    def __init__(self, tela: pygame.Surface):
        self.tela = tela

        # --- Carrega fontes monoespaçadas ---
        try:
            self.fonte_grande  = pygame.font.SysFont("Courier New", 52, bold=True)
            self.fonte_media   = pygame.font.SysFont("Courier New", 28, bold=True)
            self.fonte_pequena = pygame.font.SysFont("Courier New", 20)
        except Exception:
            self.fonte_grande  = pygame.font.Font(None, 60)
            self.fonte_media   = pygame.font.Font(None, 36)
            self.fonte_pequena = pygame.font.Font(None, 24)

    # -------------------------------------------------------------------------
    # HUD em jogo
    # -------------------------------------------------------------------------

    def desenhar_hud(self, pontuacao: int, fase: int = 1,
                     duplo_canhao: bool = False, banner_timer: int = 0):
        """Desenha pontuação, barra de velocidade e indicadores de fase."""

        # --- Pontuação ---
        texto_pts = self.fonte_media.render(f"SCORE  {pontuacao:05d}", True, COLOR_HUD)
        self.tela.blit(texto_pts, (16, 12))

        # --- Indicador de velocidade ---
        velocidade_atual = ASTEROID_BASE_SPEED + pontuacao * ASTEROID_SPEED_INCREMENT
        nivel = min(int((velocidade_atual - ASTEROID_BASE_SPEED) / 0.5) + 1, 10)
        texto_vel = self.fonte_pequena.render(f"SPEED  LVL {nivel}", True, COLOR_ACCENT)
        self.tela.blit(texto_vel, (16, 46))

        # Barra segmentada de velocidade
        self._desenhar_barra_velocidade(nivel, x=16, y=70)

        # --- Indicador de Fase 2 ---
        if fase == 2:
            fase_surf = self.fonte_pequena.render("[ FASE 2 ]", True, COLOR_FASE2)
            self.tela.blit(fase_surf, (16, 84))

        # --- Ícone de duplo canhão ativo ---
        if duplo_canhao:
            dc_surf = self.fonte_pequena.render(">> DUPLO CANHAO <<", True, COLOR_POWERUP)
            self.tela.blit(dc_surf, (SCREEN_WIDTH - dc_surf.get_width() - 16, 12))

        # --- Banner de transição "Duplo Canhão Ativado" ---
        if banner_timer > 0:
            self._desenhar_banner_duplo_canhao(banner_timer)

    def _desenhar_barra_velocidade(self, nivel: int, x: int, y: int):
        """Barra segmentada com até 10 divisões indicando dificuldade."""
        larg = 14
        alt  = 6
        gap  = 3
        for i in range(10):
            cor  = COLOR_ACCENT if i < nivel else (30, 60, 80)
            rect = pygame.Rect(x + i * (larg + gap), y, larg, alt)
            pygame.draw.rect(self.tela, cor, rect, border_radius=2)

    def _desenhar_banner_duplo_canhao(self, timer: int):
        """Banner animado que aparece ao ativar o duplo canhão."""
        # Fade: aparece nos primeiros 30 frames, some nos últimos 30
        DURACAO_TOTAL = 180  # frames (~3 segundos)
        alpha = 255
        if timer > DURACAO_TOTAL - 30:
            alpha = int(255 * (DURACAO_TOTAL - timer) / 30)
        elif timer < 30:
            alpha = int(255 * timer / 30)

        alpha = max(0, min(255, alpha))

        surf_banner = pygame.Surface((500, 60), pygame.SRCALPHA)
        surf_banner.fill((0, 0, 0, int(alpha * 0.6)))

        texto = self.fonte_media.render("★  DUPLO CANHAO ATIVADO  ★", True,
                                         (*COLOR_POWERUP, alpha))
        tx = (surf_banner.get_width()  - texto.get_width())  // 2
        ty = (surf_banner.get_height() - texto.get_height()) // 2
        surf_banner.blit(texto, (tx, ty))

        bx = (SCREEN_WIDTH  - surf_banner.get_width())  // 2
        by = SCREEN_HEIGHT // 2 - 100
        self.tela.blit(surf_banner, (bx, by))

    # -------------------------------------------------------------------------
    # Tela de início
    # -------------------------------------------------------------------------

    def desenhar_tela_inicio(self, frame: int):
        """Tela de boas-vindas com animação de piscar."""

        # Título
        titulo = self.fonte_grande.render("ASTEROID BLAST", True, COLOR_TITLE)
        self.tela.blit(titulo, titulo.get_rect(center=(SCREEN_WIDTH // 2,
                                                        SCREEN_HEIGHT // 2 - 80)))

        # Linha decorativa
        larg = titulo.get_width()
        cx   = SCREEN_WIDTH // 2
        pygame.draw.line(self.tela, COLOR_ACCENT,
                         (cx - larg // 2, SCREEN_HEIGHT // 2 - 46),
                         (cx + larg // 2, SCREEN_HEIGHT // 2 - 46), 2)

        # Instruções
        instrucoes = [
            "SETAS  -  MOVER NAVE",
            "ESPACO  -  DISPARAR",
        ]
        for i, linha in enumerate(instrucoes):
            surf = self.fonte_pequena.render(linha, True, COLOR_HUD)
            self.tela.blit(surf, surf.get_rect(center=(SCREEN_WIDTH // 2,
                                                        SCREEN_HEIGHT // 2 + i * 30)))

        # "Pressione espaço" piscando
        if (frame // 40) % 2 == 0:
            press = self.fonte_media.render("PRESSIONE ESPACO PARA INICIAR", True, COLOR_PLAYER)
            self.tela.blit(press, press.get_rect(center=(SCREEN_WIDTH // 2,
                                                          SCREEN_HEIGHT // 2 + 130)))

    # -------------------------------------------------------------------------
    # Tela de Game Over
    # -------------------------------------------------------------------------

    def desenhar_game_over(self, pontuacao: int, frame: int, fase: int = 1):
        """Tela de Game Over com overlay, pontuação e opção de reinício."""

        # Overlay escuro
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.tela.blit(overlay, (0, 0))

        # GAME OVER
        go_surf = self.fonte_grande.render("GAME  OVER", True, COLOR_GAMEOVER)
        self.tela.blit(go_surf, go_surf.get_rect(center=(SCREEN_WIDTH // 2,
                                                           SCREEN_HEIGHT // 2 - 80)))

        # Pontuação final
        pts_surf = self.fonte_media.render(f"PONTUACAO FINAL:  {pontuacao:05d}", True, COLOR_HUD)
        self.tela.blit(pts_surf, pts_surf.get_rect(center=(SCREEN_WIDTH // 2,
                                                             SCREEN_HEIGHT // 2)))

        # Fase alcançada
        fase_surf = self.fonte_pequena.render(f"FASE ALCANCADA:  {fase}", True, COLOR_ACCENT)
        self.tela.blit(fase_surf, fase_surf.get_rect(center=(SCREEN_WIDTH // 2,
                                                               SCREEN_HEIGHT // 2 + 36)))

        # Opções piscando
        if (frame // 40) % 2 == 0:
            r_surf = self.fonte_media.render("R - JOGAR NOVAMENTE    ESC - SAIR",
                                              True, COLOR_ACCENT)
            self.tela.blit(r_surf, r_surf.get_rect(center=(SCREEN_WIDTH // 2,
                                                             SCREEN_HEIGHT // 2 + 80)))
