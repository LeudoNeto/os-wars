"""
Gerenciador da interface do usuário
"""

import pygame
from game.utils.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WHITE, BLACK, GRAY, DARK_GRAY,
    PLAYER_INFO_X, PLAYER_INFO_Y, PHASE_DISPLAY_X, PHASE_DISPLAY_Y,
    BUTTON_X, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT,
    LOGO_SIZE, PHASE_ATTACK, PHASE_EVENT
)


class UIManager:
    """Gerencia os elementos da interface do usuário"""
    
    def __init__(self, screen, logos):
        """
        Inicializa o gerenciador de UI.
        
        Args:
            screen: Surface do pygame
            logos: Dicionário com as logos dos jogadores
        """
        self.screen = screen
        self.logos = logos
        
        # Fontes
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 20)
        
        # Botão
        self.button_rect = pygame.Rect(BUTTON_X, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.button_hovered = False
    
    def render_bottom_panel(self, current_player, current_phase, attacks_info, 
                           total_control, show_button=True, event_finished=False,
                           selected_attack_continent=None):
        """
        Renderiza o painel inferior com informações do jogo.
        
        Args:
            current_player: Objeto Player atual
            current_phase: Fase atual (PHASE_ATTACK ou PHASE_EVENT)
            attacks_info: Dicionário com informações dos ataques
            total_control: Porcentagem total de controle do jogador
            show_button: Se deve mostrar o botão
            event_finished: Se o evento já terminou (para mudar botão para "Passar Turno")
            selected_attack_continent: Continente selecionado para ataque (ou None)
        """
        # Não desenha mais o fundo preto/cinza
        
        # Informações do jogador (esquerda)
        self._render_player_info(current_player, total_control, attacks_info, current_phase)
        
        # Fases (parte inferior, uma ao lado da outra)
        self._render_phases(current_phase)
        
        # Botão (direita)
        if show_button:
            self._render_button(current_phase, event_finished, selected_attack_continent)
    
    def _render_player_info(self, player, total_control, attacks_info, current_phase):
        """Renderiza informações do jogador atual"""
        # Logo do jogador
        if player.name in self.logos:
            logo = pygame.transform.scale(self.logos[player.name], LOGO_SIZE)
            logo_rect = logo.get_rect(center=(PLAYER_INFO_X, PLAYER_INFO_Y))
            self.screen.blit(logo, logo_rect)
        
        # Nome do jogador
        name_text = self.font_large.render(player.name, True, player.color)
        name_rect = name_text.get_rect(topleft=(PLAYER_INFO_X - 40, PLAYER_INFO_Y + 50))
        self.screen.blit(name_text, name_rect)
        
        # Controle total
        control_text = self.font_medium.render(
            f"Controle: {total_control:.1f}%", True, WHITE
        )
        control_rect = control_text.get_rect(topleft=(PLAYER_INFO_X - 40, PLAYER_INFO_Y + 85))
        self.screen.blit(control_text, control_rect)
        
        # Habilidade especial
        ability_text = self.font_small.render(
            f"Habilidade: {player.ability}", True, GRAY
        )
        ability_rect = ability_text.get_rect(topleft=(PLAYER_INFO_X - 40, PLAYER_INFO_Y + 115))
        self.screen.blit(ability_text, ability_rect)
        
        # Ataques restantes (se estiver na fase de ataque)
        if current_phase == PHASE_ATTACK:
            attacks_text = self.font_small.render(
                f"Ataques: {attacks_info['remaining']}/{attacks_info['total']}", True, WHITE
            )
            attacks_rect = attacks_text.get_rect(topleft=(PLAYER_INFO_X - 40, PLAYER_INFO_Y + 140))
            self.screen.blit(attacks_text, attacks_rect)
    
    def _render_phases(self, current_phase):
        """Renderiza as fases do turno na parte inferior"""
        phases = [PHASE_ATTACK, PHASE_EVENT]
        
        # Posição na parte inferior da tela, centralizadas horizontalmente
        y_pos = WINDOW_HEIGHT - 60
        spacing = 280  # Espaço entre as duas fases
        
        # Centraliza horizontalmente: calcula posição inicial considerando o espaçamento
        total_width = spacing  # Distância entre os centros das duas fases
        start_x = (WINDOW_WIDTH // 2) - (spacing // 2)
        
        for i, phase in enumerate(phases):
            is_current = phase == current_phase
            
            # Cor baseada se é a fase atual
            color = WHITE if is_current else DARK_GRAY
            bg_color = (50, 50, 100) if is_current else (30, 30, 30)
            
            # Posição horizontal
            x_pos = start_x + (i * spacing)
            
            # Desenha fundo da fase
            phase_rect = pygame.Rect(x_pos - 120, y_pos - 5, 240, 40)
            pygame.draw.rect(self.screen, bg_color, phase_rect)
            pygame.draw.rect(self.screen, color, phase_rect, 2)
            
            # Texto da fase
            phase_text = self.font_medium.render(phase, True, color)
            phase_text_rect = phase_text.get_rect(center=(x_pos, y_pos + 15))
            self.screen.blit(phase_text, phase_text_rect)
    
    def _render_button(self, current_phase, event_finished=False, selected_attack_continent=None):
        """Renderiza o botão de passar fase/turno ou cancelar ataque"""
        # Texto do botão baseado na fase e estado
        if current_phase == PHASE_ATTACK:
            if selected_attack_continent:
                button_text = "Cancelar Ataque"
            else:
                button_text = "Passar Etapa"
        elif event_finished:
            button_text = "Passar Turno"
        else:
            button_text = "Girar Roleta"
        
        # Cor baseada em hover
        button_color = WHITE if self.button_hovered else GRAY
        bg_color = DARK_GRAY if self.button_hovered else BLACK
        
        # Desenha botão
        pygame.draw.rect(self.screen, bg_color, self.button_rect)
        pygame.draw.rect(self.screen, button_color, self.button_rect, 3)
        
        # Texto
        text = self.font_medium.render(button_text, True, button_color)
        text_rect = text.get_rect(center=self.button_rect.center)
        self.screen.blit(text, text_rect)
    
    def update_button_hover(self, mouse_pos):
        """
        Atualiza estado de hover do botão.
        
        Args:
            mouse_pos: Posição do mouse
        """
        self.button_hovered = self.button_rect.collidepoint(mouse_pos)
    
    def is_button_clicked(self, mouse_pos):
        """
        Verifica se o botão foi clicado.
        
        Args:
            mouse_pos: Posição do clique
            
        Returns:
            True se o botão foi clicado
        """
        return self.button_rect.collidepoint(mouse_pos)
    
    def render_combat_result(self, combat_result):
        """
        Renderiza o resultado de um combate.
        
        Args:
            combat_result: Dicionário com resultado do combate
        """
        if not combat_result:
            return
        
        # Cria painel central
        panel_width = 500
        panel_height = 400
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
        # Fundo semi-transparente
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Painel
        pygame.draw.rect(self.screen, BLACK, panel_rect)
        pygame.draw.rect(self.screen, WHITE, panel_rect, 3)
        
        # Título
        title = self.font_large.render("Resultado do Combate", True, WHITE)
        title_rect = title.get_rect(center=(panel_x + panel_width//2, panel_y + 30))
        self.screen.blit(title, title_rect)
        
        y = panel_y + 80
        
        # Informações do combate
        lines = [
            f"Atacante: {combat_result['attacker']}",
            f"Dados: {combat_result['attacker_dice']}",
            "",
            f"Defensor: {combat_result['defender']}",
            f"Dados: {combat_result['defender_dice']}",
            "",
            f"Vitórias do Atacante: {combat_result['attacker_wins']}",
            f"Controle Ganho: {combat_result['control_gained']}%",
            "",
            f"Novo controle do {combat_result['attacker']}: {combat_result['new_attacker_control']}%",
            f"Novo controle do {combat_result['defender']}: {combat_result['new_defender_control']}%"
        ]
        
        for line in lines:
            if line:
                text = self.font_small.render(line, True, WHITE)
                text_rect = text.get_rect(center=(panel_x + panel_width//2, y))
                self.screen.blit(text, text_rect)
            y += 25
        
        # Instrução
        instruction = self.font_small.render(
            "Clique para continuar", True, GRAY
        )
        instruction_rect = instruction.get_rect(
            center=(panel_x + panel_width//2, panel_y + panel_height - 30)
        )
        self.screen.blit(instruction, instruction_rect)
    
    def render_game_over(self, winner, total_control):
        """
        Renderiza a tela de fim de jogo.
        
        Args:
            winner: Nome do jogador vencedor
            total_control: Porcentagem de controle do vencedor
        """
        # Overlay semi-transparente
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Título
        title_font = pygame.font.Font(None, 72)
        title = title_font.render("FIM DE JOGO!", True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 250))
        self.screen.blit(title, title_rect)
        
        # Vencedor
        winner_text = self.font_large.render(
            f"{winner} Venceu!", True, WHITE
        )
        winner_rect = winner_text.get_rect(center=(WINDOW_WIDTH//2, 350))
        self.screen.blit(winner_text, winner_rect)
        
        # Controle
        control_text = self.font_medium.render(
            f"Controle Total: {total_control:.1f}%", True, WHITE
        )
        control_rect = control_text.get_rect(center=(WINDOW_WIDTH//2, 420))
        self.screen.blit(control_text, control_rect)
        
        # Instrução
        instruction = self.font_small.render(
            "Pressione ESC para sair", True, GRAY
        )
        instruction_rect = instruction.get_rect(center=(WINDOW_WIDTH//2, 500))
        self.screen.blit(instruction, instruction_rect)
    
    def render_enemy_selection(self, enemies, target_continent):
        """
        Renderiza popup de seleção de inimigo para atacar.
        
        Args:
            enemies: Lista de objetos Player inimigos
            target_continent: Continente sendo atacado
        """
        # Overlay semi-transparente
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Painel central
        panel_width = 500
        panel_height = 300
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, BLACK, panel_rect)
        pygame.draw.rect(self.screen, WHITE, panel_rect, 3)
        
        # Título
        title = self.font_large.render("Escolha o Inimigo", True, WHITE)
        title_rect = title.get_rect(center=(panel_x + panel_width//2, panel_y + 40))
        self.screen.blit(title, title_rect)
        
        # Subtítulo com nome do continente
        subtitle = self.font_small.render(
            f"Atacando: {target_continent.name}", True, GRAY
        )
        subtitle_rect = subtitle.get_rect(center=(panel_x + panel_width//2, panel_y + 75))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Botões dos inimigos
        button_width = 200
        button_height = 60
        spacing = 30
        start_y = panel_y + 120
        
        self.enemy_buttons = []  # Armazena rects dos botões
        
        for i, enemy in enumerate(enemies):
            button_x = panel_x + panel_width//2 - button_width//2
            button_y = start_y + i * (button_height + spacing)
            
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            self.enemy_buttons.append((button_rect, enemy))
            
            # Cor do botão
            pygame.draw.rect(self.screen, enemy.color, button_rect)
            pygame.draw.rect(self.screen, WHITE, button_rect, 2)
            
            # Nome do inimigo
            enemy_text = self.font_medium.render(enemy.name, True, WHITE)
            enemy_text_rect = enemy_text.get_rect(center=button_rect.center)
            self.screen.blit(enemy_text, enemy_text_rect)
            
            # Porcentagem no continente alvo
            control_pct = target_continent.get_control_percentage(enemy.name)
            control_text = self.font_small.render(
                f"Controle: {control_pct}%", True, WHITE
            )
            control_text_rect = control_text.get_rect(
                center=(button_rect.centerx, button_rect.centery + 25)
            )
            
            # Fundo escuro para o texto de controle
            control_bg = control_text_rect.inflate(6, 3)
            pygame.draw.rect(self.screen, BLACK, control_bg)
            
            self.screen.blit(control_text, control_text_rect)
        
        # Botão cancelar (X no canto)
        cancel_size = 30
        self.cancel_button_rect = pygame.Rect(
            panel_x + panel_width - cancel_size - 10,
            panel_y + 10,
            cancel_size,
            cancel_size
        )
        pygame.draw.rect(self.screen, (150, 0, 0), self.cancel_button_rect)
        pygame.draw.rect(self.screen, WHITE, self.cancel_button_rect, 2)
        
        # X no botão cancelar
        cancel_text = self.font_medium.render("X", True, WHITE)
        cancel_text_rect = cancel_text.get_rect(center=self.cancel_button_rect.center)
        self.screen.blit(cancel_text, cancel_text_rect)
    
    def get_clicked_enemy(self, pos, enemies):
        """
        Verifica se clicou em algum botão de inimigo.
        
        Args:
            pos: Posição do clique
            enemies: Lista de inimigos
            
        Returns:
            Objeto Player do inimigo clicado ou None
        """
        if hasattr(self, 'enemy_buttons'):
            for button_rect, enemy in self.enemy_buttons:
                if button_rect.collidepoint(pos):
                    return enemy
        return None
    
    def is_cancel_enemy_selection_clicked(self, pos):
        """
        Verifica se clicou no botão de cancelar seleção.
        
        Args:
            pos: Posição do clique
            
        Returns:
            True se clicou em cancelar
        """
        if hasattr(self, 'cancel_button_rect'):
            return self.cancel_button_rect.collidepoint(pos)
        return False
