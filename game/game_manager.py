"""
Gerenciador principal do jogo
"""

import pygame
import os
import random
from game.models.player import Player
from game.models.continent import Continent
from game.models.event import get_random_event
from game.logic.combat import CombatSystem
from game.logic.turn_manager import TurnManager
from game.ui.map_renderer import MapRenderer
from game.ui.ui_manager import UIManager
from game.ui.roulette import Roulette
from game.utils.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, WINDOW_TITLE,
    OCEAN_BLUE, PLAYERS, CONTINENTS, CONTINENT_FILES,
    LOGO_FILES, CONTINENTS_DIR, LOGOS_DIR, WIN_PERCENTAGE,
    PHASE_EVENT, BUTTON_X, BUTTON_Y
)
from game.utils.helpers import (
    distribute_initial_control, calculate_total_control, apply_event
)


class GameManager:
    """Gerenciador principal do jogo"""
    
    def __init__(self):
        """Inicializa o jogo"""
        pygame.init()
        
        # Configuração da janela
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        
        # Carrega recursos
        self.logos = self._load_logos()
        self.continents = self._load_continents()
        
        # Inicializa jogadores
        self.players = [Player(name) for name in PLAYERS]
        
        # Distribui controle inicial
        initial_control = distribute_initial_control()
        for continent in self.continents:
            continent.control = initial_control[continent.name].copy()
        
        # Sistemas de jogo
        self.combat_system = CombatSystem()
        self.turn_manager = TurnManager(self.players)
        
        # UI
        self.map_renderer = MapRenderer(self.screen, self.continents, self.logos)
        self.ui_manager = UIManager(self.screen, self.logos)
        self.roulette = Roulette(self.screen)
        
        # Estado do jogo
        self.running = True
        self.game_over = False
        self.winner = None
        
        # Estado de interação
        self.hovered_continent = None
        self.selected_attack_continent = None
        self.selected_target_continent = None
        self.showing_combat_result = False
        self.showing_roulette = False
        self.showing_event_result = False
        self.showing_enemy_selection = False
        self.event_applied_continent = None
        self.event_result = None  # Dados do resultado do evento
        self.event_finished = False  # Indica se o evento já terminou e aguarda "Passar Turno"
        
        # Inicia o primeiro turno
        max_attacks = self.combat_system.get_max_attacks_for_player(
            self.turn_manager.get_current_player().name,
            self.continents
        )
        self.turn_manager.start_turn(max_attacks)
    
    def _load_logos(self):
        """Carrega as logos dos jogadores"""
        logos = {}
        for player, filename in LOGO_FILES.items():
            path = os.path.join(LOGOS_DIR, filename)
            try:
                logos[player] = pygame.image.load(path).convert_alpha()
            except Exception as e:
                print(f"Erro ao carregar logo {player}: {e}")
                # Cria placeholder
                logo = pygame.Surface((80, 80), pygame.SRCALPHA)
                logo.fill((100, 100, 100, 200))
                logos[player] = logo
        return logos
    
    def _load_continents(self):
        """Carrega os continentes"""
        continents = []
        for continent_name in CONTINENTS:
            filename = CONTINENT_FILES[continent_name]
            path = os.path.join(CONTINENTS_DIR, filename)
            continent = Continent(continent_name, path)
            continents.append(continent)
        return continents
    
    def run(self):
        """Loop principal do jogo"""
        while self.running:
            self._handle_events()
            self._update()
            self._render()
            self.clock.tick(FPS)
        
        pygame.quit()
    
    def _handle_events(self):
        """Processa eventos"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Botão esquerdo
                    self._handle_click(event.pos)
            
            elif event.type == pygame.MOUSEMOTION:
                self._handle_mouse_motion(event.pos)
    
    def _handle_click(self, pos):
        """Trata cliques do mouse"""
        # Se está mostrando seleção de inimigo
        if self.showing_enemy_selection:
            self._handle_enemy_selection_click(pos)
            return
        
        # Se está mostrando resultado de combate
        if self.showing_combat_result:
            self.showing_combat_result = False
            self.combat_system.clear_last_result()
            self._check_win_condition()
            return
        
        # Se está mostrando resultado de evento
        if self.showing_event_result:
            self.showing_event_result = False
            self.showing_roulette = False
            self.event_applied_continent = None
            self.event_result = None
            # Marca que o evento terminou, mas não passa turno ainda
            self.event_finished = True
            return
        
        # Se está mostrando a roleta
        if self.showing_roulette:
            if not self.roulette.is_spinning():
                # Aplica evento
                self._apply_random_event()
            return
        
        # Se o jogo acabou
        if self.game_over:
            return
        
        # Verifica clique no botão
        if self.ui_manager.is_button_clicked(pos):
            self._handle_button_click()
            return
        
        # Fase de ataque - seleção de continentes
        if self.turn_manager.is_attack_phase():
            clicked_continent = self.map_renderer.get_continent_at_position(pos)
            
            if clicked_continent:
                self._handle_continent_click(clicked_continent)
    
    def _handle_button_click(self):
        """Trata clique no botão"""
        if self.turn_manager.is_attack_phase():
            # Passa para fase de evento
            self.turn_manager.skip_attack_phase()
            self.selected_attack_continent = None
        
        elif self.turn_manager.is_event_phase():
            # Se o evento já terminou, passa o turno
            if self.event_finished:
                self.event_finished = False
                self._next_turn()
            else:
                # Inicia roleta
                self.showing_roulette = True
                self.roulette.start_spin()
    
    def _handle_continent_click(self, continent):
        """Trata clique em um continente"""
        current_player = self.turn_manager.get_current_player()
        
        # Verifica se ainda tem ataques disponíveis
        if not self.turn_manager.can_attack():
            return
        
        # Se não há continente selecionado, seleciona como atacante
        if not self.selected_attack_continent:
            # Agora pode selecionar qualquer continente como atacante
            self.selected_attack_continent = continent
        else:
            # Já tem um atacante, este é o alvo
            target_continent = continent
            
            # Verifica se é válido atacar
            if self._can_attack(self.selected_attack_continent, target_continent):
                # Mostra popup de seleção de inimigo
                self.selected_target_continent = target_continent
                self.showing_enemy_selection = True
            else:
                # Limpa seleção se ataque inválido
                self.selected_attack_continent = None
    
    def _can_attack(self, attacker_continent, target_continent):
        """Verifica se um ataque é válido"""
        current_player = self.turn_manager.get_current_player()
        
        # Pode atacar o próprio continente ou adjacentes
        if target_continent == attacker_continent:
            return True
        
        if attacker_continent.is_adjacent_to(target_continent):
            return True
        
        return False
    
    def _handle_enemy_selection_click(self, pos):
        """Trata clique na seleção de inimigo"""
        current_player = self.turn_manager.get_current_player()
        
        # Obtém os inimigos (jogadores que não são o atual)
        enemies = [p for p in self.players if p.name != current_player.name]
        
        # Verifica se clicou em algum botão de inimigo
        selected_enemy = self.ui_manager.get_clicked_enemy(pos, enemies)
        
        if selected_enemy:
            # Executa ataque contra o inimigo selecionado
            self._execute_attack(self.selected_target_continent, selected_enemy)
            
            # Fecha popup e limpa seleções
            self.showing_enemy_selection = False
            self.selected_attack_continent = None
            self.selected_target_continent = None
        elif self.ui_manager.is_cancel_enemy_selection_clicked(pos):
            # Cancela seleção
            self.showing_enemy_selection = False
            self.selected_attack_continent = None
            self.selected_target_continent = None
    
    def _execute_attack(self, target_continent, defender):
        """Executa um ataque"""
        current_player = self.turn_manager.get_current_player()
        
        # Executa combate
        result = self.combat_system.execute_attack(
            current_player,
            defender,
            self.selected_attack_continent,
            target_continent
        )
        
        # Usa um ataque
        self.turn_manager.use_attack()
        
        # Mostra resultado
        self.showing_combat_result = True
    
    def _apply_random_event(self):
        """Aplica o evento aleatório selecionado"""
        event = self.roulette.get_selected_event()
        current_player = self.turn_manager.get_current_player()
        
        # Seleciona continente aleatório
        continent = random.choice(self.continents)
        self.event_applied_continent = continent
        
        # Salva controle antes do evento
        control_before = {player: continent.control[player] for player in continent.control}
        
        # Aplica evento
        apply_event(continent.control, current_player.name, event.percentage)
        
        # Salva controle depois do evento
        control_after = {player: continent.control[player] for player in continent.control}
        
        # Armazena resultado completo
        self.event_result = {
            'event': event,
            'continent': continent,
            'player': current_player.name,
            'control_before': control_before,
            'control_after': control_after
        }
        
        # Mostra resultado
        self.showing_event_result = True
    
    def _next_turn(self):
        """Avança para o próximo turno"""
        self.turn_manager.next_turn()
        
        # Calcula ataques máximos para o novo jogador
        current_player = self.turn_manager.get_current_player()
        max_attacks = self.combat_system.get_max_attacks_for_player(
            current_player.name,
            self.continents
        )
        self.turn_manager.start_turn(max_attacks)
        
        # Verifica condição de vitória
        self._check_win_condition()
    
    def _check_win_condition(self):
        """Verifica se algum jogador venceu"""
        for player in self.players:
            total_control = calculate_total_control(
                {c.name: c.control for c in self.continents},
                player.name
            )
            
            if total_control >= WIN_PERCENTAGE:
                self.game_over = True
                self.winner = player
                return
    
    def _handle_mouse_motion(self, pos):
        """Trata movimento do mouse"""
        # Atualiza hover do botão
        self.ui_manager.update_button_hover(pos)
        
        # Atualiza continente sob o mouse
        if not self.showing_roulette and not self.showing_combat_result:
            self.hovered_continent = self.map_renderer.get_continent_at_position(pos)
    
    def _update(self):
        """Atualiza estado do jogo"""
        # Atualiza roleta se estiver girando
        if self.showing_roulette and self.roulette.is_spinning():
            self.roulette.update()
    
    def _render(self):
        """Renderiza o jogo"""
        # Fundo
        self.screen.fill(OCEAN_BLUE)
        
        # Mapa
        highlight = self.selected_attack_continent if self.selected_attack_continent else self.hovered_continent
        self.map_renderer.render(highlight)
        
        # Destaque do continente selecionado para ataque
        if self.selected_attack_continent and not self.showing_combat_result:
            rect = self.selected_attack_continent.rect
            pygame.draw.rect(self.screen, (255, 255, 0), rect, 4)
        
        # Painel inferior (sempre visível)
        current_player = self.turn_manager.get_current_player()
        total_control = calculate_total_control(
            {c.name: c.control for c in self.continents},
            current_player.name
        )
        
        # Mostra botão apenas se não há hover em continente e não está em combate
        show_button = not (self.hovered_continent and not self.showing_combat_result) and not self.showing_combat_result
        
        self.ui_manager.render_bottom_panel(
            current_player,
            self.turn_manager.get_current_phase(),
            self.turn_manager.get_attacks_info(),
            total_control,
            show_button=show_button,
            event_finished=self.event_finished
        )
        
        # Gráfico de pizza se hover sobre continente
        if self.hovered_continent and not self.showing_roulette and not self.showing_combat_result:
            self.map_renderer.render_pie_chart(
                self.hovered_continent,
                (BUTTON_X + 90, 720)  # Posição Y fixa para não cortar o gráfico
            )
        
        # Seleção de inimigo
        if self.showing_enemy_selection:
            current_player = self.turn_manager.get_current_player()
            enemies = [p for p in self.players if p.name != current_player.name]
            self.ui_manager.render_enemy_selection(
                enemies,
                self.selected_target_continent
            )
        
        # Resultado de combate
        if self.showing_combat_result:
            self.ui_manager.render_combat_result(
                self.combat_system.last_combat_result
            )
        
        # Roleta
        if self.showing_roulette:
            show_result = not self.roulette.is_spinning()
            self.roulette.render(show_result, self.event_result)
        
        # Game Over
        if self.game_over and self.winner:
            total_control = calculate_total_control(
                {c.name: c.control for c in self.continents},
                self.winner.name
            )
            self.ui_manager.render_game_over(self.winner.name, total_control)
        
        # Atualiza tela
        pygame.display.flip()
