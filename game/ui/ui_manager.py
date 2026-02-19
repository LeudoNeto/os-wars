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
        
        # Estado do menu: controle por player ou IA
        self.os_control_mode = {
            "Windows": "player",
            "MacOS": "player",
            "Linux": "player"
        }
    
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
    
    def render_combat_result(self, combat_result, animation_elapsed, animation_duration):
        """
        Renderiza o resultado de um combate com dados ordenados e gráfico de pizza animado.
        
        Args:
            combat_result: Dicionário com resultado do combate
            animation_elapsed: Tempo decorrido da animação
            animation_duration: Duração total da animação
        """
        if not combat_result:
            return
        
        # Calcula progresso da animação (0.0 a 1.0)
        animation_progress = min(1.0, animation_elapsed / animation_duration)
        
        # Fundo semi-transparente
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Painel central maior
        panel_width = 900
        panel_height = 600
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, BLACK, panel_rect)
        pygame.draw.rect(self.screen, WHITE, panel_rect, 3)
        
        # Título
        title = self.font_large.render("Resultado do Combate", True, WHITE)
        title_rect = title.get_rect(center=(panel_x + panel_width//2, panel_y + 40))
        self.screen.blit(title, title_rect)
        
        # Continente
        continent_text = self.font_medium.render(
            f"Continente: {combat_result['defending_continent']}", 
            True, WHITE
        )
        continent_rect = continent_text.get_rect(center=(panel_x + panel_width//2, panel_y + 80))
        self.screen.blit(continent_text, continent_rect)
        
        # Posição dos dados (esquerda e direita)
        left_x = panel_x + 120
        right_x = panel_x + panel_width - 120
        dice_y_start = panel_y + 180
        
        # Renderiza dados do atacante (esquerda) - ordenados em ordem decrescente
        attacker_label = self.font_medium.render(
            combat_result['attacker'], 
            True, combat_result['attacker_color']
        )
        attacker_label_rect = attacker_label.get_rect(center=(left_x, panel_y + 130))
        self.screen.blit(attacker_label, attacker_label_rect)
        
        self._render_sorted_dice_vertical(
            left_x, dice_y_start,
            combat_result['attacker_dice'],
            combat_result['attacker_color']
        )
        
        # Renderiza dados do defensor (direita) - ordenados em ordem decrescente
        defender_label = self.font_medium.render(
            combat_result['defender'], 
            True, combat_result['defender_color']
        )
        defender_label_rect = defender_label.get_rect(center=(right_x, panel_y + 130))
        self.screen.blit(defender_label, defender_label_rect)
        
        self._render_sorted_dice_vertical(
            right_x, dice_y_start,
            combat_result['defender_dice'],
            combat_result['defender_color']
        )
        
        # Gráfico de pizza animado no centro
        pie_center_x = panel_x + panel_width // 2
        pie_center_y = panel_y + 320
        pie_radius = 100
        
        self._render_animated_pie_chart(
            pie_center_x, pie_center_y, pie_radius,
            combat_result['control_before'],
            combat_result['control_after'],
            animation_progress
        )
        
        # Resultado do combate
        result_y = panel_y + 480
        result_text = f"Vitórias do Atacante: {combat_result['attacker_wins']} | Controle Ganho: {combat_result['control_gained']}%"
        result = self.font_small.render(result_text, True, WHITE)
        result_rect = result.get_rect(center=(panel_x + panel_width//2, result_y))
        self.screen.blit(result, result_rect)
        
        # Instrução
        instruction = self.font_small.render(
            "Clique para continuar", True, GRAY
        )
        instruction_rect = instruction.get_rect(
            center=(panel_x + panel_width//2, panel_y + panel_height - 30)
        )
        self.screen.blit(instruction, instruction_rect)
    
    def _render_sorted_dice_vertical(self, center_x, start_y, dice_values, color):
        """Renderiza dados verticalmente já ordenados em ordem decrescente"""
        dice_size = 60
        spacing = 15
        
        for i, value in enumerate(dice_values):
            y = start_y + i * (dice_size + spacing)
            self._draw_3d_die(center_x, y, dice_size, value, color, angle=0, scale=1.0)
    
    def _render_animated_pie_chart(self, center_x, center_y, radius, 
                                   control_before, control_after, progress):
        """Renderiza gráfico de pizza com animação de transição"""
        from game.utils.constants import PLAYER_COLORS
        import math
        
        # Interpola entre controle antes e depois
        current_control = {}
        for player in control_before:
            before_val = control_before[player]
            after_val = control_after[player]
            current_control[player] = before_val + (after_val - before_val) * progress
        
        # Normaliza para somar 100
        total = sum(current_control.values())
        if total > 0:
            current_control = {p: (v / total) * 100 for p, v in current_control.items()}
        
        # Desenha o gráfico de pizza
        start_angle = 0
        for player, percentage in sorted(current_control.items(), key=lambda x: x[1], reverse=True):
            if percentage > 0:
                color = PLAYER_COLORS.get(player, (128, 128, 128))
                angle = (percentage / 100.0) * 360
                
                # Desenha fatia
                self._draw_pie_slice(
                    center_x, center_y, radius,
                    start_angle, start_angle + angle,
                    color
                )
                
                # Desenha label se a fatia for grande o suficiente
                if percentage >= 5:
                    mid_angle = math.radians(start_angle + angle / 2 - 90)
                    label_distance = radius * 0.7
                    label_x = center_x + label_distance * math.cos(mid_angle)
                    label_y = center_y + label_distance * math.sin(mid_angle)
                    
                    label_text = self.font_small.render(f"{percentage:.0f}%", True, WHITE)
                    label_rect = label_text.get_rect(center=(label_x, label_y))
                    self.screen.blit(label_text, label_rect)
                
                start_angle += angle
        
        # Borda do círculo
        pygame.draw.circle(self.screen, WHITE, (center_x, center_y), radius, 3)
    
    def _draw_pie_slice(self, center_x, center_y, radius, start_angle, end_angle, color):
        """Desenha uma fatia do gráfico de pizza"""
        import math
        
        # Converte ângulos para radianos
        start_rad = math.radians(start_angle - 90)
        end_rad = math.radians(end_angle - 90)
        
        # Cria lista de pontos para o polígono
        points = [(center_x, center_y)]
        
        # Adiciona pontos ao longo do arco
        num_points = max(3, int((end_angle - start_angle) / 2))
        for i in range(num_points + 1):
            angle = start_rad + (end_rad - start_rad) * i / num_points
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append((x, y))
        
        # Desenha o polígono
        if len(points) >= 3:
            pygame.draw.polygon(self.screen, color, points)
            pygame.draw.polygon(self.screen, WHITE, points, 2)
    
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
    
    def render_combat_preparation(self, attacker, defender, attacker_dice, defender_dice,
                                   max_attacker_dice, max_defender_dice, logos):
        """
        Renderiza a tela de preparação de combate.
        
        Args:
            attacker: Jogador atacante
            defender: Jogador defensor
            attacker_dice: Quantidade de dados do atacante
            defender_dice: Quantidade de dados do defensor
            max_attacker_dice: Máximo de dados do atacante
            max_defender_dice: Máximo de dados do defensor
            logos: Dicionário com logos dos jogadores
        """
        # Overlay semi-transparente
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Painel central
        panel_width = 800
        panel_height = 500
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, BLACK, panel_rect)
        pygame.draw.rect(self.screen, WHITE, panel_rect, 3)
        
        # Título
        title = self.font_large.render("Preparação de Combate", True, WHITE)
        title_rect = title.get_rect(center=(panel_x + panel_width//2, panel_y + 40))
        self.screen.blit(title, title_rect)
        
        # Logo e info do atacante (esquerda)
        attacker_x = panel_x + 150
        attacker_y = panel_y + 150
        
        if attacker.name in logos:
            logo = pygame.transform.scale(logos[attacker.name], (100, 100))
            logo_rect = logo.get_rect(center=(attacker_x, attacker_y))
            self.screen.blit(logo, logo_rect)
        
        attacker_label = self.font_medium.render("Atacante", True, WHITE)
        attacker_label_rect = attacker_label.get_rect(center=(attacker_x, attacker_y - 90))
        self.screen.blit(attacker_label, attacker_label_rect)
        
        attacker_name = self.font_small.render(attacker.name, True, attacker.color)
        attacker_name_rect = attacker_name.get_rect(center=(attacker_x, attacker_y + 70))
        self.screen.blit(attacker_name, attacker_name_rect)
        
        # Logo e info do defensor (direita)
        defender_x = panel_x + panel_width - 150
        defender_y = panel_y + 150
        
        if defender.name in logos:
            logo = pygame.transform.scale(logos[defender.name], (100, 100))
            logo_rect = logo.get_rect(center=(defender_x, defender_y))
            self.screen.blit(logo, logo_rect)
        
        defender_label = self.font_medium.render("Defensor", True, WHITE)
        defender_label_rect = defender_label.get_rect(center=(defender_x, defender_y - 90))
        self.screen.blit(defender_label, defender_label_rect)
        
        defender_name = self.font_small.render(defender.name, True, defender.color)
        defender_name_rect = defender_name.get_rect(center=(defender_x, defender_y + 70))
        self.screen.blit(defender_name, defender_name_rect)
        
        # Seletores de dados
        selector_y = panel_y + 320
        
        # Seletor do atacante
        self._render_dice_selector(
            attacker_x, selector_y, attacker_dice, max_attacker_dice,
            attacker.color, "attacker"
        )
        
        # Seletor do defensor
        self._render_dice_selector(
            defender_x, selector_y, defender_dice, max_defender_dice,
            defender.color, "defender"
        )
        
        # Botão Rolar (centro)
        roll_button_width = 180
        roll_button_height = 60
        roll_button_x = panel_x + (panel_width - roll_button_width) // 2
        roll_button_y = panel_y + panel_height - 100
        
        self.roll_button_rect = pygame.Rect(
            roll_button_x, roll_button_y, roll_button_width, roll_button_height
        )
        
        pygame.draw.rect(self.screen, (0, 150, 0), self.roll_button_rect)
        pygame.draw.rect(self.screen, WHITE, self.roll_button_rect, 3)
        
        roll_text = self.font_large.render("ROLAR", True, WHITE)
        roll_text_rect = roll_text.get_rect(center=self.roll_button_rect.center)
        self.screen.blit(roll_text, roll_text_rect)
    
    def _render_dice_selector(self, center_x, center_y, dice_count, max_dice, color, side):
        """Renderiza um seletor de dados com botões + e -"""
        from game.utils.constants import MIN_DICE
        
        # Número de dados
        dice_text = self.font_large.render(str(dice_count), True, WHITE)
        dice_rect = dice_text.get_rect(center=(center_x, center_y))
        self.screen.blit(dice_text, dice_rect)
        
        # Label "Dados"
        label = self.font_small.render("Dados", True, GRAY)
        label_rect = label.get_rect(center=(center_x, center_y - 40))
        self.screen.blit(label, label_rect)
        
        # Botão + (acima)
        button_size = 40
        plus_button = pygame.Rect(
            center_x - button_size//2,
            center_y - 70,
            button_size,
            button_size
        )
        
        # Desabilita se já está no máximo
        plus_enabled = dice_count < max_dice
        plus_color = color if plus_enabled else DARK_GRAY
        
        pygame.draw.rect(self.screen, plus_color, plus_button)
        pygame.draw.rect(self.screen, WHITE, plus_button, 2)
        
        plus_text = self.font_medium.render("+", True, WHITE)
        plus_text_rect = plus_text.get_rect(center=plus_button.center)
        self.screen.blit(plus_text, plus_text_rect)
        
        # Botão - (abaixo)
        minus_button = pygame.Rect(
            center_x - button_size//2,
            center_y + 40,
            button_size,
            button_size
        )
        
        # Desabilita se já está no mínimo
        minus_enabled = dice_count > MIN_DICE
        minus_color = color if minus_enabled else DARK_GRAY
        
        pygame.draw.rect(self.screen, minus_color, minus_button)
        pygame.draw.rect(self.screen, WHITE, minus_button, 2)
        
        minus_text = self.font_medium.render("-", True, WHITE)
        minus_text_rect = minus_text.get_rect(center=minus_button.center)
        self.screen.blit(minus_text, minus_text_rect)
        
        # Salva referências dos botões
        if side == "attacker":
            self.attacker_plus_button = plus_button if plus_enabled else None
            self.attacker_minus_button = minus_button if minus_enabled else None
        else:
            self.defender_plus_button = plus_button if plus_enabled else None
            self.defender_minus_button = minus_button if minus_enabled else None
    
    def handle_combat_preparation_click(self, pos, attacker_dice, defender_dice,
                                        max_attacker_dice, max_defender_dice):
        """
        Trata cliques na tela de preparação de combate.
        
        Args:
            pos: Posição do clique
            attacker_dice: Quantidade atual de dados do atacante
            defender_dice: Quantidade atual de dados do defensor
            max_attacker_dice: Máximo de dados do atacante
            max_defender_dice: Máximo de dados do defensor
            
        Returns:
            String indicando a ação: "attacker_increase", "attacker_decrease",
            "defender_increase", "defender_decrease", "roll", ou None
        """
        from game.utils.constants import MIN_DICE
        
        # Verifica botão de rolar
        if hasattr(self, 'roll_button_rect') and self.roll_button_rect.collidepoint(pos):
            return "roll"
        
        # Verifica botões do atacante
        if hasattr(self, 'attacker_plus_button') and self.attacker_plus_button:
            if self.attacker_plus_button.collidepoint(pos) and attacker_dice < max_attacker_dice:
                return "attacker_increase"
        
        if hasattr(self, 'attacker_minus_button') and self.attacker_minus_button:
            if self.attacker_minus_button.collidepoint(pos) and attacker_dice > MIN_DICE:
                return "attacker_decrease"
        
        # Verifica botões do defensor
        if hasattr(self, 'defender_plus_button') and self.defender_plus_button:
            if self.defender_plus_button.collidepoint(pos) and defender_dice < max_defender_dice:
                return "defender_increase"
        
        if hasattr(self, 'defender_minus_button') and self.defender_minus_button:
            if self.defender_minus_button.collidepoint(pos) and defender_dice > MIN_DICE:
                return "defender_decrease"
        
        return None
    
    def render_dice_animation(self, attacker, defender, attacker_dice_count, 
                              defender_dice_count, elapsed_time, logos):
        """Renderiza animação dos dados girando"""
        import random
        
        # Overlay semi-transparente
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Painel central (mais alto para acomodar grid de dados)
        panel_width = 800
        panel_height = 550
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, BLACK, panel_rect)
        pygame.draw.rect(self.screen, WHITE, panel_rect, 3)
        
        # Título
        title = self.font_large.render("Rolando Dados...", True, WHITE)
        title_rect = title.get_rect(center=(panel_x + panel_width//2, panel_y + 50))
        self.screen.blit(title, title_rect)
        
        # Dados do atacante (esquerda)
        self._render_animated_dice(
            panel_x + 150, panel_y + 280,
            attacker_dice_count, attacker.color, "Atacante"
        )
        
        # Dados do defensor (direita)
        self._render_animated_dice(
            panel_x + panel_width - 150, panel_y + 280,
            defender_dice_count, defender.color, "Defensor"
        )
    
    def _render_animated_dice(self, center_x, center_y, dice_count, color, label):
        """Renderiza dados animados (valores aleatórios) com aparência 3D em grid 2 colunas"""
        import random
        import math
        
        # Label
        label_text = self.font_medium.render(label, True, WHITE)
        label_rect = label_text.get_rect(center=(center_x, center_y - 140))
        self.screen.blit(label_text, label_rect)
        
        # Configuração do grid de dados
        dice_size = 60
        spacing_x = 20  # Espaçamento horizontal entre colunas
        spacing_y = 15  # Espaçamento vertical entre linhas
        cols = 2  # 2 colunas
        
        # Calcula número de linhas necessárias
        rows = (dice_count + cols - 1) // cols  # Arredonda para cima
        
        # Posição inicial (centralizada)
        grid_width = cols * dice_size + (cols - 1) * spacing_x
        grid_height = rows * dice_size + (rows - 1) * spacing_y
        start_x = center_x - grid_width // 2 + dice_size // 2
        start_y = center_y - grid_height // 2 + dice_size // 2
        
        # Fator de rotação baseado no tempo para animação
        rotation_factor = pygame.time.get_ticks() / 100.0
        
        for i in range(dice_count):
            row = i // cols
            col = i % cols
            
            x = start_x + col * (dice_size + spacing_x)
            y = start_y + row * (dice_size + spacing_y)
            
            # Valor aleatório para animação
            value = random.randint(1, 6)
            
            # Oscilação para efeito de rotação
            angle = math.sin(rotation_factor + i) * 15
            scale_factor = 1.0 + math.cos(rotation_factor + i * 0.5) * 0.1
            
            # Desenha dado 3D
            self._draw_3d_die(x, y, dice_size, value, color, angle, scale_factor)
    
    def _draw_3d_die(self, center_x, center_y, size, value, color, angle=0, scale=1.0):
        """Desenha um dado com aparência 3D e pontinhos"""
        import math
        
        # Aplica escala
        actual_size = int(size * scale)
        
        # Sombra
        shadow_offset = 4
        shadow_rect = pygame.Rect(
            center_x - actual_size//2 + shadow_offset,
            center_y - actual_size//2 + shadow_offset,
            actual_size, actual_size
        )
        shadow_surface = pygame.Surface((actual_size, actual_size), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 100), shadow_surface.get_rect(), border_radius=8)
        self.screen.blit(shadow_surface, shadow_rect)
        
        # Corpo do dado (cor do jogador)
        dice_rect = pygame.Rect(
            center_x - actual_size//2,
            center_y - actual_size//2,
            actual_size, actual_size
        )
        
        # Fundo da cor do jogador
        pygame.draw.rect(self.screen, color, dice_rect, border_radius=8)
        
        # Borda mais escura para destaque
        darker_color = tuple(max(0, c - 40) for c in color)
        pygame.draw.rect(self.screen, darker_color, dice_rect, 3, border_radius=8)
        
        # Efeito de brilho mais intenso (canto superior esquerdo)
        shine_surface = pygame.Surface((actual_size//2, actual_size//2), pygame.SRCALPHA)
        pygame.draw.rect(shine_surface, (255, 255, 255, 80), shine_surface.get_rect(), border_radius=4)
        self.screen.blit(shine_surface, (dice_rect.x + 5, dice_rect.y + 5))
        
        # Desenha os pontinhos
        self._draw_die_pips(dice_rect, value, color)
    
    def _draw_die_pips(self, dice_rect, value, color):
        """Desenha os pontinhos (pips) do dado baseado no valor"""
        pip_radius = max(4, dice_rect.width // 12)
        pip_color = WHITE  # Branco para contrastar com a cor do dado
        
        cx = dice_rect.centerx
        cy = dice_rect.centery
        offset = dice_rect.width // 4
        
        # Para valores acima de 6 (bônus do MacOS), desenha o número
        if value > 6:
            # Desenha o número no centro do dado
            font_size = dice_rect.width // 2
            font = pygame.font.Font(None, font_size)
            number_text = font.render(str(value), True, WHITE)
            number_rect = number_text.get_rect(center=(cx, cy))
            
            # Sombra do número
            shadow_text = font.render(str(value), True, (0, 0, 0, 100))
            shadow_rect = shadow_text.get_rect(center=(cx + 2, cy + 2))
            self.screen.blit(shadow_text, shadow_rect)
            
            # Número principal
            self.screen.blit(number_text, number_rect)
            return
        
        # Posições dos pontinhos
        positions = {
            'center': (cx, cy),
            'top_left': (cx - offset, cy - offset),
            'top_right': (cx + offset, cy - offset),
            'middle_left': (cx - offset, cy),
            'middle_right': (cx + offset, cy),
            'bottom_left': (cx - offset, cy + offset),
            'bottom_right': (cx + offset, cy + offset),
        }
        
        # Define quais pontinhos desenhar para cada valor
        pip_patterns = {
            1: ['center'],
            2: ['top_left', 'bottom_right'],
            3: ['top_left', 'center', 'bottom_right'],
            4: ['top_left', 'top_right', 'bottom_left', 'bottom_right'],
            5: ['top_left', 'top_right', 'center', 'bottom_left', 'bottom_right'],
            6: ['top_left', 'top_right', 'middle_left', 'middle_right', 'bottom_left', 'bottom_right'],
        }
        
        # Desenha os pontinhos
        for pip_name in pip_patterns.get(value, []):
            pos = positions[pip_name]
            # Sombra do pontinho para profundidade
            pygame.draw.circle(self.screen, (0, 0, 0, 80), 
                             (pos[0] + 1, pos[1] + 1), pip_radius)
            # Pontinho principal (branco)
            pygame.draw.circle(self.screen, pip_color, pos, pip_radius)
            # Brilho no pontinho
            pygame.draw.circle(self.screen, (255, 255, 255), 
                             (pos[0] - pip_radius//4, pos[1] - pip_radius//4), 
                             pip_radius//4)
    
    def render_dice_results(self, attacker, defender, attacker_dice, defender_dice, logos):
        """Renderiza resultados dos dados com opção de re-roll para Linux"""
        # Overlay semi-transparente
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Painel central (mais alto para acomodar grid de dados)
        panel_width = 800
        panel_height = 650
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, BLACK, panel_rect)
        pygame.draw.rect(self.screen, WHITE, panel_rect, 3)
        
        # Título
        title = self.font_large.render("Resultados dos Dados", True, WHITE)
        title_rect = title.get_rect(center=(panel_x + panel_width//2, panel_y + 40))
        self.screen.blit(title, title_rect)
        
        # Dados do atacante (esquerda)
        attacker_can_reroll = attacker.can_reroll()
        self.attacker_dice_rects = self._render_result_dice(
            panel_x + 150, panel_y + 310,
            attacker_dice, attacker.color, attacker.name,
            attacker_can_reroll, "attacker"
        )
        
        # Dados do defensor (direita)
        defender_can_reroll = defender.can_reroll()
        self.defender_dice_rects = self._render_result_dice(
            panel_x + panel_width - 150, panel_y + 310,
            defender_dice, defender.color, defender.name,
            defender_can_reroll, "defender"
        )
        
        # Instruções de re-roll se aplicável
        if attacker_can_reroll or defender_can_reroll:
            instruction = self.font_small.render(
                "Linux: Clique em um dado para re-rolar (1x por combate)",
                True, (46, 204, 113)
            )
            instruction_rect = instruction.get_rect(
                center=(panel_x + panel_width//2, panel_y + panel_height - 100)
            )
            self.screen.blit(instruction, instruction_rect)
        
        # Botão Continuar
        button_width = 200
        button_height = 60
        button_x = panel_x + (panel_width - button_width) // 2
        button_y = panel_y + panel_height - 70
        
        self.continue_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, (0, 100, 200), self.continue_button_rect)
        pygame.draw.rect(self.screen, WHITE, self.continue_button_rect, 3)
        
        continue_text = self.font_medium.render("Continuar", True, WHITE)
        continue_text_rect = continue_text.get_rect(center=self.continue_button_rect.center)
        self.screen.blit(continue_text, continue_text_rect)
    
    def _render_result_dice(self, center_x, center_y, dice_values, color, player_name,
                            can_reroll, side):
        """Renderiza dados com valores finais (clicáveis se Linux) em grid 2 colunas"""
        # Nome do jogador
        name_text = self.font_medium.render(player_name, True, color)
        name_rect = name_text.get_rect(center=(center_x, center_y - 140))
        self.screen.blit(name_text, name_rect)
        
        # Configuração do grid de dados
        dice_size = 60
        spacing_x = 20  # Espaçamento horizontal entre colunas
        spacing_y = 15  # Espaçamento vertical entre linhas
        cols = 2  # 2 colunas
        dice_count = len(dice_values)
        
        # Calcula número de linhas necessárias
        rows = (dice_count + cols - 1) // cols  # Arredonda para cima
        
        # Posição inicial (centralizada)
        grid_width = cols * dice_size + (cols - 1) * spacing_x
        grid_height = rows * dice_size + (rows - 1) * spacing_y
        start_x = center_x - grid_width // 2 + dice_size // 2
        start_y = center_y - grid_height // 2 + dice_size // 2
        
        dice_rects = []
        
        for i, value in enumerate(dice_values):
            row = i // cols
            col = i % cols
            
            x = start_x + col * (dice_size + spacing_x)
            y = start_y + row * (dice_size + spacing_y)
            
            # Desenha dado 3D
            scale = 1.05 if can_reroll else 1.0  # Ligeiramente maior se clicável
            self._draw_3d_die(x, y, dice_size, value, color, angle=0, scale=scale)
            
            # Adiciona um indicador visual se for clicável (brilho extra)
            if can_reroll:
                dice_rect = pygame.Rect(
                    x - dice_size//2,
                    y - dice_size//2,
                    dice_size, dice_size
                )
                # Overlay pulsante para indicar que é clicável
                pulse = abs(pygame.time.get_ticks() % 1000 - 500) / 500.0  # 0 a 1
                overlay = pygame.Surface((dice_size, dice_size), pygame.SRCALPHA)
                alpha = int(30 + pulse * 30)  # 30 a 60
                pygame.draw.rect(overlay, (255, 255, 255, alpha), overlay.get_rect(), border_radius=8)
                self.screen.blit(overlay, dice_rect)
            
            # Armazena retângulo para detecção de clique
            dice_rect = pygame.Rect(x - dice_size//2, y - dice_size//2, dice_size, dice_size)
            dice_rects.append((dice_rect, i))
        
        return dice_rects
    
    def handle_dice_results_click(self, pos, attacker, defender, attacker_dice, defender_dice):
        """Trata cliques na tela de resultados dos dados
        
        Returns:
            String indicando ação: "reroll_attacker_X", "reroll_defender_X", "continue", ou None
        """
        # Verifica botão continuar
        if hasattr(self, 'continue_button_rect') and self.continue_button_rect.collidepoint(pos):
            return "continue"
        
        # Verifica clique em dados do atacante (se pode re-rolar)
        if attacker.can_reroll() and hasattr(self, 'attacker_dice_rects'):
            for dice_rect, dice_index in self.attacker_dice_rects:
                if dice_rect.collidepoint(pos):
                    return f"reroll_attacker_{dice_index}"
        
        # Verifica clique em dados do defensor (se pode re-rolar)
        if defender.can_reroll() and hasattr(self, 'defender_dice_rects'):
            for dice_rect, dice_index in self.defender_dice_rects:
                if dice_rect.collidepoint(pos):
                    return f"reroll_defender_{dice_index}"
        
        return None
    
    def render_turn_confirmation(self):
        """Renderiza popup de confirmação para passar turno"""
        # Overlay semi-transparente
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Painel central
        panel_width = 400
        panel_height = 200
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, BLACK, panel_rect)
        pygame.draw.rect(self.screen, WHITE, panel_rect, 3)
        
        # Título
        title = self.font_large.render("Confirmar", True, WHITE)
        title_rect = title.get_rect(center=(panel_x + panel_width//2, panel_y + 40))
        self.screen.blit(title, title_rect)
        
        # Texto de confirmação
        text = self.font_medium.render("Deseja realmente passar o turno?", True, WHITE)
        text_rect = text.get_rect(center=(panel_x + panel_width//2, panel_y + 90))
        self.screen.blit(text, text_rect)
        
        # Botões
        button_width = 120
        button_height = 40
        button_y = panel_y + panel_height - 60
        
        # Botão SIM (verde)
        yes_button_x = panel_x + (panel_width // 2) - button_width - 10
        self.yes_button_rect = pygame.Rect(yes_button_x, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, (0, 150, 0), self.yes_button_rect)
        pygame.draw.rect(self.screen, WHITE, self.yes_button_rect, 2)
        
        yes_text = self.font_medium.render("Sim", True, WHITE)
        yes_text_rect = yes_text.get_rect(center=self.yes_button_rect.center)
        self.screen.blit(yes_text, yes_text_rect)
        
        # Botão NÃO (vermelho)
        no_button_x = panel_x + (panel_width // 2) + 10
        self.no_button_rect = pygame.Rect(no_button_x, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, (150, 0, 0), self.no_button_rect)
        pygame.draw.rect(self.screen, WHITE, self.no_button_rect, 2)
        
        no_text = self.font_medium.render("Não", True, WHITE)
        no_text_rect = no_text.get_rect(center=self.no_button_rect.center)
        self.screen.blit(no_text, no_text_rect)
    
    def handle_turn_confirmation_click(self, pos):
        """
        Trata cliques na confirmação de passar turno
        
        Returns:
            "yes" se clicou em Sim, "no" se clicou em Não, None caso contrário
        """
        if hasattr(self, 'yes_button_rect') and self.yes_button_rect.collidepoint(pos):
            return "yes"
        if hasattr(self, 'no_button_rect') and self.no_button_rect.collidepoint(pos):
            return "no"
        return None
    
    def render_main_menu(self, map_surface=None):
        """Renderiza o menu principal
        
        Args:
            map_surface: Surface opcional com o mapa renderizado para usar como fundo
        """
        # Mapa com blur no fundo
        if map_surface:
            # Cria overlay escuro semi-transparente
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.fill((0, 0, 30))
            overlay.set_alpha(200)
            self.screen.blit(map_surface, (0, 0))
            self.screen.blit(overlay, (0, 0))
        
        # Logo do jogo no topo
        if "game" in self.logos and self.logos["game"]:
            logo = self.logos["game"]
            # Escala para um tamanho adequado
            logo_width, logo_height = logo.get_size()
            max_logo_height = 300
            if logo_height > max_logo_height:
                scale_factor = max_logo_height / logo_height
                new_width = int(logo_width * scale_factor)
                logo = pygame.transform.scale(logo, (new_width, max_logo_height))
            
            logo_rect = logo.get_rect(center=(WINDOW_WIDTH // 2, 180))
            self.screen.blit(logo, logo_rect)
        else:
            # Fallback: título em texto
            title_font = pygame.font.Font(None, 72)
            title_text = title_font.render("OS WARS", True, WHITE)
            title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 180))
            self.screen.blit(title_text, title_rect)
        
        # Cards dos sistemas operacionais
        card_width = 350
        card_height = 250
        card_spacing = 50
        total_cards_width = 3 * card_width + 2 * card_spacing
        start_x = (WINDOW_WIDTH - total_cards_width) // 2
        card_y = 380
        
        # Informações dos SOs
        os_info = {
            "Windows": {
                "ability": "Ataca com 1 dado extra",
                "color": (0, 150, 255)
            },
            "MacOS": {
                "ability": "Defende com +1 em todos os dados",
                "color": (128, 128, 128)
            },
            "Linux": {
                "ability": "Re-rola 1 dado por combate",
                "color": (255, 165, 0)
            }
        }
        
        os_names = ["Windows", "MacOS", "Linux"]
        self.os_card_rects = {}  # Armazena retângulos dos cards para detecção de clique
        self.os_icon_rects = {}  # Armazena retângulos dos ícones player/IA
        
        for i, os_name in enumerate(os_names):
            card_x = start_x + i * (card_width + card_spacing)
            
            # Fundo do card (borda uniforme para todos)
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            self.os_card_rects[os_name] = card_rect
            pygame.draw.rect(self.screen, (30, 30, 50), card_rect)
            pygame.draw.rect(self.screen, (100, 100, 120), card_rect, 3)
            
            # Logo do SO
            if os_name in self.logos:
                logo = pygame.transform.scale(self.logos[os_name], (100, 100))
                logo_rect = logo.get_rect(center=(card_x + card_width // 2, card_y + 70))
                self.screen.blit(logo, logo_rect)
            
            # Nome do SO
            name_text = self.font_large.render(os_name, True, os_info[os_name]["color"])
            name_rect = name_text.get_rect(center=(card_x + card_width // 2, card_y + 145))
            self.screen.blit(name_text, name_rect)
            
            # Habilidade especial (quebra em duas linhas se necessário)
            ability = os_info[os_name]["ability"]
            # Divide o texto em palavras
            words = ability.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + word + " "
                test_surface = self.font_small.render(test_line, True, WHITE)
                if test_surface.get_width() <= card_width - 20:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line.strip())
                    current_line = word + " "
            if current_line:
                lines.append(current_line.strip())
            
            # Renderiza as linhas
            for j, line in enumerate(lines):
                ability_text = self.font_small.render(line, True, WHITE)
                ability_rect = ability_text.get_rect(
                    center=(card_x + card_width // 2, card_y + 180 + j * 25)
                )
                self.screen.blit(ability_text, ability_rect)
            
            # Ícone de player/IA no canto inferior direito
            icon_size = 40
            icon_x = card_x + card_width - icon_size - 10
            icon_y = card_y + card_height - icon_size - 10
            icon_rect = pygame.Rect(icon_x, icon_y, icon_size, icon_size)
            self.os_icon_rects[os_name] = icon_rect
            
            # Desenha o ícone baseado no modo
            mode = self.os_control_mode[os_name]
            if mode == "player":
                # Ícone de jogador (pessoa simplificada)
                pygame.draw.rect(self.screen, (50, 50, 70), icon_rect)
                pygame.draw.rect(self.screen, (0, 200, 0), icon_rect, 2)
                # Cabeça
                pygame.draw.circle(self.screen, (0, 200, 0), 
                                 (icon_x + icon_size // 2, icon_y + 12), 6)
                # Corpo
                pygame.draw.line(self.screen, (0, 200, 0),
                               (icon_x + icon_size // 2, icon_y + 18),
                               (icon_x + icon_size // 2, icon_y + 30), 2)
                # Braços
                pygame.draw.line(self.screen, (0, 200, 0),
                               (icon_x + icon_size // 2 - 6, icon_y + 22),
                               (icon_x + icon_size // 2 + 6, icon_y + 22), 2)
                # Pernas
                pygame.draw.line(self.screen, (0, 200, 0),
                               (icon_x + icon_size // 2, icon_y + 30),
                               (icon_x + icon_size // 2 - 5, icon_y + 36), 2)
                pygame.draw.line(self.screen, (0, 200, 0),
                               (icon_x + icon_size // 2, icon_y + 30),
                               (icon_x + icon_size // 2 + 5, icon_y + 36), 2)
            else:  # IA/robô
                # Ícone de robô
                pygame.draw.rect(self.screen, (50, 50, 70), icon_rect)
                pygame.draw.rect(self.screen, (200, 0, 0), icon_rect, 2)
                # Cabeça (quadrado)
                head_rect = pygame.Rect(icon_x + 10, icon_y + 8, 20, 16)
                pygame.draw.rect(self.screen, (200, 0, 0), head_rect, 2)
                # Olhos
                pygame.draw.circle(self.screen, (200, 0, 0),
                                 (icon_x + 16, icon_y + 16), 2)
                pygame.draw.circle(self.screen, (200, 0, 0),
                                 (icon_x + 24, icon_y + 16), 2)
                # Corpo
                body_rect = pygame.Rect(icon_x + 8, icon_y + 24, 24, 12)
                pygame.draw.rect(self.screen, (200, 0, 0), body_rect, 2)
        
        # Botão "Jogar"
        button_width = 300
        button_height = 60
        button_x = (WINDOW_WIDTH - button_width) // 2
        button_y = card_y + card_height + 60
        
        self.play_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, (0, 150, 0), self.play_button_rect)
        pygame.draw.rect(self.screen, WHITE, self.play_button_rect, 3)
        
        play_text = self.font_large.render("Jogar", True, WHITE)
        play_text_rect = play_text.get_rect(center=self.play_button_rect.center)
        self.screen.blit(play_text, play_text_rect)
    
    def handle_main_menu_click(self, pos):
        """
        Trata cliques no menu principal
        
        Returns:
            True se clicou no botão Jogar, False caso contrário
        """
        # Verifica clique nos ícones de player/IA
        if hasattr(self, 'os_icon_rects'):
            for os_name, icon_rect in self.os_icon_rects.items():
                if icon_rect.collidepoint(pos):
                    # Alterna entre player e IA
                    if self.os_control_mode[os_name] == "player":
                        self.os_control_mode[os_name] = "ai"
                    else:
                        self.os_control_mode[os_name] = "player"
                    return False  # Não inicia o jogo, apenas alterna
        
        # Verifica clique no botão Jogar
        if hasattr(self, 'play_button_rect') and self.play_button_rect.collidepoint(pos):
            return True
        return False
