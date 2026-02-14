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
        
        # Painel central
        panel_width = 800
        panel_height = 500
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
            panel_x + 150, panel_y + 250,
            attacker_dice_count, attacker.color, "Atacante"
        )
        
        # Dados do defensor (direita)
        self._render_animated_dice(
            panel_x + panel_width - 150, panel_y + 250,
            defender_dice_count, defender.color, "Defensor"
        )
    
    def _render_animated_dice(self, center_x, center_y, dice_count, color, label):
        """Renderiza dados animados (valores aleatórios)"""
        import random
        
        # Label
        label_text = self.font_medium.render(label, True, WHITE)
        label_rect = label_text.get_rect(center=(center_x, center_y - 100))
        self.screen.blit(label_text, label_rect)
        
        # Renderiza cada dado
        dice_size = 50
        spacing = 10
        start_y = center_y - ((dice_count * (dice_size + spacing)) // 2)
        
        for i in range(dice_count):
            y = start_y + i * (dice_size + spacing)
            
            # Valor aleatório para animação
            value = random.randint(1, 6)
            
            # Desenha dado
            dice_rect = pygame.Rect(center_x - dice_size//2, y, dice_size, dice_size)
            pygame.draw.rect(self.screen, color, dice_rect)
            pygame.draw.rect(self.screen, WHITE, dice_rect, 2)
            
            # Valor
            value_text = self.font_medium.render(str(value), True, WHITE)
            value_rect = value_text.get_rect(center=dice_rect.center)
            self.screen.blit(value_text, value_rect)
    
    def render_dice_results(self, attacker, defender, attacker_dice, defender_dice, logos):
        """Renderiza resultados dos dados com opção de re-roll para Linux"""
        # Overlay semi-transparente
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Painel central
        panel_width = 800
        panel_height = 600
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
            panel_x + 150, panel_y + 250,
            attacker_dice, attacker.color, attacker.name,
            attacker_can_reroll, "attacker"
        )
        
        # Dados do defensor (direita)
        defender_can_reroll = defender.can_reroll()
        self.defender_dice_rects = self._render_result_dice(
            panel_x + panel_width - 150, panel_y + 250,
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
        """Renderiza dados com valores finais (clicáveis se Linux)"""
        # Nome do jogador
        name_text = self.font_medium.render(player_name, True, color)
        name_rect = name_text.get_rect(center=(center_x, center_y - 120))
        self.screen.blit(name_text, name_rect)
        
        # Renderiza cada dado
        dice_size = 50
        spacing = 10
        dice_count = len(dice_values)
        start_y = center_y - ((dice_count * (dice_size + spacing)) // 2)
        
        dice_rects = []
        
        for i, value in enumerate(dice_values):
            y = start_y + i * (dice_size + spacing)
            
            # Desenha dado
            dice_rect = pygame.Rect(center_x - dice_size//2, y, dice_size, dice_size)
            pygame.draw.rect(self.screen, color, dice_rect)
            
            # Borda mais grossa se clicável
            border_width = 3 if can_reroll else 2
            pygame.draw.rect(self.screen, WHITE, dice_rect, border_width)
            
            # Valor
            value_text = self.font_medium.render(str(value), True, WHITE)
            value_rect = value_text.get_rect(center=dice_rect.center)
            self.screen.blit(value_text, value_rect)
            
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
