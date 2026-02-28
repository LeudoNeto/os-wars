"""
Gerenciador principal do jogo
"""

import pygame
import os
import random
import math
from game.models.player import Player
from game.models.continent import Continent
from game.models.event import get_random_event
from game.logic.combat import CombatSystem
from game.logic.turn_manager import TurnManager
from game.ui.map_renderer import MapRenderer
from game.ui.ui_manager import UIManager
from game.ui.roulette import Roulette
from game.utils.audio_manager import AudioManager
from game.utils.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, WINDOW_TITLE,
    OCEAN_BLUE, PLAYERS, CONTINENTS, CONTINENT_FILES,
    LOGO_FILES, CONTINENTS_DIR, LOGOS_DIR, WIN_PERCENTAGE,
    PHASE_EVENT, BUTTON_X, BUTTON_Y, PLAYER_COLORS, CONTINENT_INFO_OFFSET,
    MUSIC_MENU, MUSIC_GAME, MUSIC_COMBAT,
    SOUND_CLICK, SOUND_DICE_ROLL, SOUND_CONQUEST, SOUND_ROULETTE,
    ADJACENT_CONTINENTS
)
from game.utils.helpers import (
    distribute_initial_control, calculate_total_control, apply_event
)

# RL - importação condicional
try:
    from game.rl.rl_agent import RLAgent, ACTION_SPACE, NUM_ACTIONS
    RL_AVAILABLE = True
except ImportError:
    RL_AVAILABLE = False


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
        
        # Inicializa jogadores (será configurado ao iniciar o jogo)
        self.players = [Player(name) for name in PLAYERS]
        
        # Estado da IA
        self.ai_action_timer = 0
        self.ai_waiting = False
        self.ai_action_delay = 2.0  # 2 segundos entre ações
        
        # Agentes RL (inicializados ao clicar "Jogar")
        self.rl_agents = {}  # {player_name: RLAgent}
        
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
        
        # Áudio
        self.audio_manager = AudioManager()
        
        # Estado do jogo
        self.running = True
        self.showing_main_menu = True
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
        self.showing_turn_confirmation = False  # Mostra confirmação de passar turno
        
        # Preparação de combate
        self.preparing_combat = False
        self.showing_dice_animation = False
        self.showing_dice_results = False
        self.selected_enemy = None
        self.attacker_dice_count = 1
        self.defender_dice_count = 1
        self.max_attacker_dice = 1
        self.max_defender_dice = 1
        self.attacker_dice_results = []
        self.defender_dice_results = []
        self.dice_animation_start = 0
        self.current_attacker = None
        self.current_defender = None
        self.current_attack_continent = None
        self.current_target_continent = None
        
        # Animação do resultado
        self.combat_result_animation_start = 0
        self.combat_result_animation_duration = 3.0  # 2 segundos de animação
        self.machine_gun_count = 0  # Conta quantas vezes tocou o som de conquista
        
        # Animação
        self.animation_offset = 0  # Offset para animar as setas
        
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
        
        # Carrega logo do jogo para o menu
        game_logo_path = os.path.join(LOGOS_DIR, "oswars.png")
        try:
            logos["game"] = pygame.image.load(game_logo_path).convert_alpha()
        except Exception as e:
            print(f"Erro ao carregar logo do jogo: {e}")
            logos["game"] = None
        
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
        import time
        
        # Inicia música do menu
        self.audio_manager.play_music(MUSIC_MENU)
        
        while self.running:
            # Atualiza animação
            self.animation_offset = (self.animation_offset + 2) % 60
            
            # Verifica animação de dados
            if self.showing_dice_animation:
                elapsed = time.time() - self.dice_animation_start
                if elapsed > 1.5:  # 1.5 segundos de animação
                    self.showing_dice_animation = False
                    self.showing_dice_results = True
            
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
                elif event.button == 3:  # Botão direito
                    self._handle_right_click()
            
            elif event.type == pygame.MOUSEMOTION:
                self._handle_mouse_motion(event.pos)
    
    def _handle_click(self, pos):
        """Trata cliques do mouse"""
        # Se está mostrando menu principal
        if self.showing_main_menu:
            self._handle_main_menu_click(pos)
            return
        
        # Ignora cliques durante turnos de IA ou RL
        current_player = self.turn_manager.get_current_player()
        if current_player.is_ai or current_player.is_rl:
            return
        
        # Ignora cliques durante animação de dados
        if self.showing_dice_animation:
            return
        
        # Se está mostrando confirmação de passar turno
        if self.showing_turn_confirmation:
            self._handle_turn_confirmation_click(pos)
            return
        
        # Se está mostrando resultados dos dados
        if self.showing_dice_results:
            self._handle_dice_results_click(pos)
            return
        
        # Se está preparando combate
        if self.preparing_combat:
            self._handle_combat_preparation_click(pos)
            return
        
        # Se está mostrando seleção de inimigo
        if self.showing_enemy_selection:
            self._handle_enemy_selection_click(pos)
            return
        
        # Se está mostrando resultado de combate
        if self.showing_combat_result:
            self.audio_manager.play_sound(SOUND_CLICK)
            # Volta para música do jogo
            self.audio_manager.play_music(MUSIC_GAME)
            self.showing_combat_result = False
            self.combat_system.clear_last_result()
            self._check_win_condition()
            return
        
        # Se está mostrando resultado de evento
        if self.showing_event_result:
            self.audio_manager.play_sound(SOUND_CLICK)
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
        # Som de clique
        self.audio_manager.play_sound(SOUND_CLICK)
        
        if self.turn_manager.is_attack_phase():
            # Se há continente selecionado, cancela o ataque
            if self.selected_attack_continent:
                self.selected_attack_continent = None
            else:
                # Passa para fase de evento
                self.turn_manager.skip_attack_phase()
                self.selected_attack_continent = None
        
        elif self.turn_manager.is_event_phase():
            # Se o evento já terminou, mostra confirmação antes de passar o turno
            if self.event_finished:
                self.showing_turn_confirmation = True
            else:
                # Carrega eventos do jogador atual
                current_player = self.turn_manager.get_current_player()
                self.roulette.set_player_events(current_player.name)
                
                # Inicia roleta
                self.showing_roulette = True
                self.roulette.start_spin()
                # Toca som da roleta (limitado a 3 segundos)
                self.audio_manager.play_sound_limited(SOUND_ROULETTE, 1200)
                # Toca som da roleta (limitado a 3 segundos)
                self.audio_manager.play_sound_limited(SOUND_ROULETTE, 1200)
    
    def _handle_turn_confirmation_click(self, pos):
        """Trata cliques na confirmação de passar turno"""
        action = self.ui_manager.handle_turn_confirmation_click(pos)
        
        if action == "yes":
            self.audio_manager.play_sound(SOUND_CLICK)
            # Confirma passar o turno
            self.showing_turn_confirmation = False
            self.event_finished = False
            self._next_turn()
        elif action == "no":
            self.audio_manager.play_sound(SOUND_CLICK)
            # Cancela e volta ao jogo
            self.showing_turn_confirmation = False
    
    def _handle_main_menu_click(self, pos):
        """Trata cliques no menu principal"""
        action = self.ui_manager.handle_main_menu_click(pos)
        
        if action == "play":
            # Toca som de clique
            self.audio_manager.play_sound(SOUND_CLICK)
            # Configura jogadores baseado no modo selecionado
            for player in self.players:
                mode = self.ui_manager.os_control_mode[player.name]
                player.is_ai = (mode == "ai")
                player.is_rl = (mode == "rl")
            # Inicializa agentes RL para jogadores com modo RL
            self._init_rl_agents()
            # Inicia o jogo
            self.showing_main_menu = False
            # Muda para música do jogo
            self.audio_manager.play_music(MUSIC_GAME)
        elif action == "toggle":
            # Toca som de clique ao alternar player/IA
            self.audio_manager.play_sound(SOUND_CLICK)
    
    def _handle_right_click(self):
        """Trata clique com botão direito"""
        # Não permite cancelar se já está em alguma etapa avançada do ataque
        if (self.showing_enemy_selection or self.preparing_combat or 
            self.showing_dice_animation or self.showing_dice_results or 
            self.showing_combat_result):
            return
        
        # Se está na fase de ataque e há continente selecionado, cancela
        if self.turn_manager.is_attack_phase() and self.selected_attack_continent:
            self.selected_attack_continent = None
    
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
            # Som de clique
            self.audio_manager.play_sound(SOUND_CLICK)
            # Vai para preparação de combate
            self.showing_enemy_selection = False
            self._prepare_combat(selected_enemy)
        elif self.ui_manager.is_cancel_enemy_selection_clicked(pos):
            # Som de clique
            self.audio_manager.play_sound(SOUND_CLICK)
            # Cancela seleção
            self.showing_enemy_selection = False
            self.selected_attack_continent = None
            self.selected_target_continent = None
    
    def _prepare_combat(self, defender):
        """Prepara o combate, calculando máximo de dados para cada lado"""
        current_player = self.turn_manager.get_current_player()
        
        # Música de combate
        self.audio_manager.play_music(MUSIC_COMBAT)
        
        # Reseta habilidade de re-roll para ambos os jogadores (1 vez por combate)
        current_player.ability_used = False
        defender.ability_used = False
        
        # Calcula quantidade de dados para cada lado
        from game.utils.helpers import calculate_dice_count
        from game.utils.constants import MIN_DICE
        
        attacker_control = self.selected_attack_continent.get_control_percentage(current_player.name)
        defender_control = self.selected_target_continent.get_control_percentage(defender.name)
        
        # Calcula máximo de dados com bônus especiais
        self.max_attacker_dice = calculate_dice_count(
            attacker_control, 
            bonus=current_player.get_attack_bonus()
        )
        self.max_defender_dice = calculate_dice_count(defender_control)
        
        # Inicializa com os valores máximos
        self.attacker_dice_count = self.max_attacker_dice
        self.defender_dice_count = self.max_defender_dice
        
        self.selected_enemy = defender
        self.preparing_combat = True
    
    def _handle_combat_preparation_click(self, pos):
        """Trata cliques na tela de preparação de combate"""
        action = self.ui_manager.handle_combat_preparation_click(
            pos,
            self.attacker_dice_count,
            self.defender_dice_count,
            self.max_attacker_dice,
            self.max_defender_dice
        )
        
        if action == "attacker_increase":
            self.audio_manager.play_sound(SOUND_CLICK)
            self.attacker_dice_count = min(self.attacker_dice_count + 1, self.max_attacker_dice)
        elif action == "attacker_decrease":
            self.audio_manager.play_sound(SOUND_CLICK)
            from game.utils.constants import MIN_DICE
            self.attacker_dice_count = max(self.attacker_dice_count - 1, MIN_DICE)
        elif action == "defender_increase":
            self.audio_manager.play_sound(SOUND_CLICK)
            self.defender_dice_count = min(self.defender_dice_count + 1, self.max_defender_dice)
        elif action == "defender_decrease":
            self.audio_manager.play_sound(SOUND_CLICK)
            from game.utils.constants import MIN_DICE
            self.defender_dice_count = max(self.defender_dice_count - 1, MIN_DICE)
        elif action == "roll":
            self.audio_manager.play_sound(SOUND_CLICK)
            # Inicia animação e rola os dados
            self._roll_dice()
    
    def _roll_dice(self):
        """Rola os dados e inicia animação"""
        from game.utils.helpers import roll_dice
        import time
        
        # Som de dados rolando
        self.audio_manager.play_sound(SOUND_DICE_ROLL)
        
        # Rola os dados
        self.attacker_dice_results = roll_dice(self.attacker_dice_count)
        self.defender_dice_results = roll_dice(self.defender_dice_count)
        
        # Aplica bônus de defesa do MacOS
        if self.selected_enemy.name == "MacOS":
            bonus = self.selected_enemy.get_defense_bonus()
            self.defender_dice_results = [d + bonus for d in self.defender_dice_results]
        
        # Guarda referências dos jogadores e continentes para o combate
        self.current_attacker = self.turn_manager.get_current_player()
        self.current_defender = self.selected_enemy
        self.current_attack_continent = self.selected_attack_continent
        self.current_target_continent = self.selected_target_continent
        
        # Inicia animação
        self.preparing_combat = False
        self.showing_dice_animation = True
        self.dice_animation_start = time.time()
    
    def _handle_dice_results_click(self, pos):
        """Trata cliques quando os dados estão sendo exibidos"""
        action = self.ui_manager.handle_dice_results_click(
            pos,
            self.current_attacker,
            self.current_defender,
            self.attacker_dice_results,
            self.defender_dice_results
        )
        
        if action and action.startswith("reroll_attacker_"):
            # Re-rola dado do atacante
            dice_index = int(action.split("_")[-1])
            if self.current_attacker.can_reroll():
                self.audio_manager.play_sound(SOUND_DICE_ROLL)
                from game.utils.helpers import roll_dice
                self.attacker_dice_results[dice_index] = roll_dice(1)[0]
                self.current_attacker.use_reroll()
        
        elif action and action.startswith("reroll_defender_"):
            # Re-rola dado do defensor
            dice_index = int(action.split("_")[-1])
            if self.current_defender.can_reroll():
                self.audio_manager.play_sound(SOUND_DICE_ROLL)
                from game.utils.helpers import roll_dice
                self.defender_dice_results[dice_index] = roll_dice(1)[0]
                self.current_defender.use_reroll()
        
        elif action == "continue":
            self.audio_manager.play_sound(SOUND_CLICK)
            # Finaliza o combate e começa animação do resultado
            import time
            self.showing_dice_results = False
            self._finish_combat()
            self.combat_result_animation_start = time.time()
    
    def _finish_combat(self):
        """Finaliza o combate aplicando os resultados"""
        from game.utils.helpers import resolve_combat, apply_combat_result
        
        # Salva controle antes do combate
        control_before = {player: self.current_target_continent.control[player] 
                         for player in self.current_target_continent.control}
        
        # Resolve o combate
        attacker_wins = resolve_combat(self.attacker_dice_results, self.defender_dice_results)
        
        # Aplica o resultado ao continente defensor
        apply_combat_result(
            self.current_target_continent.control,
            self.current_attacker.name,
            self.current_defender.name,
            attacker_wins
        )
        
        # Reseta contador do som de machine gun
        self.machine_gun_count = 0
        
        # Salva resultado para exibição
        self.combat_system.last_combat_result = {
            "attacker": self.current_attacker.name,
            "defender": self.current_defender.name,
            "attacker_color": self.current_attacker.color,
            "defender_color": self.current_defender.color,
            "attacking_continent": self.current_attack_continent.name,
            "defending_continent": self.current_target_continent.name,
            "continent": self.current_target_continent,
            "attacker_dice": sorted(self.attacker_dice_results, reverse=True),
            "defender_dice": sorted(self.defender_dice_results, reverse=True),
            "attacker_wins": attacker_wins,
            "control_gained": attacker_wins * 5,
            "control_before": control_before,
            "control_after": dict(self.current_target_continent.control),
            "new_attacker_control": self.current_target_continent.get_control_percentage(self.current_attacker.name),
            "new_defender_control": self.current_target_continent.get_control_percentage(self.current_defender.name)
        }
        
        # Usa um ataque
        self.turn_manager.use_attack()
        
        # Limpa estados de seleção
        self.selected_attack_continent = None
        self.selected_target_continent = None
        self.selected_enemy = None
        
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
    
    def _draw_attack_arrows(self, from_continent, to_continent, color):
        """Desenha setas animadas indicando trajetória de ataque"""
        # Aplica offset das informações de controle para usar como pontos da trajetória
        from_offset_x, from_offset_y = CONTINENT_INFO_OFFSET.get(from_continent.name, (0, 0))
        to_offset_x, to_offset_y = CONTINENT_INFO_OFFSET.get(to_continent.name, (0, 0))
        
        # Pontos com offset aplicado (onde ficam as porcentagens)
        start_x = from_continent.rect.centerx + from_offset_x
        start_y = from_continent.rect.centery + from_offset_y
        end_x = to_continent.rect.centerx + to_offset_x
        end_y = to_continent.rect.centery + to_offset_y
        
        # Calcula direção e distância
        dx = end_x - start_x
        dy = end_y - start_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 1:
            return
        
        # Normaliza direção
        dx /= distance
        dy /= distance
        
        # Cria fonte para as setas
        font = pygame.font.Font(None, 32)
        
        # Desenha múltiplas setas ao longo da linha
        arrow_spacing = 60  # Espaçamento entre setas
        num_arrows = int(distance / arrow_spacing) + 1
        
        for i in range(num_arrows):
            # Calcula posição base da seta
            t = (i * arrow_spacing + self.animation_offset) % distance
            
            # Se passou da distância, não desenha
            if t > distance - 20:
                continue
            
            x = start_x + dx * t
            y = start_y + dy * t
            
            # Desenha a seta ">"
            arrow_text = font.render(">", True, color)
            
            # Calcula ângulo de rotação para apontar na direção certa
            angle = math.degrees(math.atan2(dy, dx))
            rotated_arrow = pygame.transform.rotate(arrow_text, -angle)
            
            # Centraliza a seta na posição
            arrow_rect = rotated_arrow.get_rect(center=(int(x), int(y)))
            
            # Desenha a seta com um brilho
            self.screen.blit(rotated_arrow, arrow_rect)
    
    def _check_win_condition(self):
        """Verifica se algum jogador venceu"""
        for player in self.players:
            # Verifica se o jogador tem maioria (>= WIN_PERCENTAGE) em todos os continentes
            has_all_continents = True
            for continent in self.continents:
                control_percentage = continent.get_control_percentage(player.name)
                if control_percentage < WIN_PERCENTAGE:
                    has_all_continents = False
                    break
            
            if has_all_continents:
                self.game_over = True
                self.winner = player
                return
    
    def _execute_ai_action(self):
        """Executa a próxima ação da IA baseado no estado atual"""
        current_player = self.turn_manager.get_current_player()
        
        # Se está mostrando resultado de combate, apenas avança
        if self.showing_combat_result:
            print(f"[IA-{current_player.name}] Visualizando resultado do combate...")
            self.audio_manager.play_sound(SOUND_CLICK)
            self.audio_manager.play_music(MUSIC_GAME)
            self.showing_combat_result = False
            self.combat_system.clear_last_result()
            self._check_win_condition()
            return
        
        # Se está mostrando dados, trata re-roll ou continua
        if self.showing_dice_results:
            self._ai_handle_dice_results()
            return
        
        # Se está em preparação de combate, rola os dados
        if self.preparing_combat:
            print(f"[IA-{current_player.name}] Rolando dados: {self.attacker_dice_count} atacante vs {self.defender_dice_count} defensor")
            self.audio_manager.play_sound(SOUND_CLICK)
            self._roll_dice()
            return
        
        # Se está mostrando seleção de inimigo
        if self.showing_enemy_selection:
            self._ai_select_enemy()
            return
        
        # Se está mostrando resultado de evento
        if self.showing_event_result:
            print(f"[IA-{current_player.name}] Evento aplicado!")
            self.audio_manager.play_sound(SOUND_CLICK)
            self.showing_event_result = False
            self.showing_roulette = False
            self.event_applied_continent = None
            self.event_result = None
            self.event_finished = True
            return
        
        # Se está mostrando a roleta
        if self.showing_roulette:
            if not self.roulette.is_spinning():
                print(f"[IA-{current_player.name}] Aplicando evento aleatório...")
                self._apply_random_event()
            return
        
        # Se está mostrando confirmação de passar turno
        if self.showing_turn_confirmation:
            print(f"[IA-{current_player.name}] Passando o turno...")
            self.audio_manager.play_sound(SOUND_CLICK)
            self.showing_turn_confirmation = False
            self.event_finished = False
            self._next_turn()
            return
        
        # Fase de ataque
        if self.turn_manager.is_attack_phase():
            if self.turn_manager.can_attack():
                self._ai_execute_attack()
            else:
                # Não tem mais ataques, passa para fase de evento
                print(f"[IA-{current_player.name}] Sem mais ataques. Passando para fase de evento...")
                self.audio_manager.play_sound(SOUND_CLICK)
                self.turn_manager.skip_attack_phase()
                self.selected_attack_continent = None
            return
        
        # Fase de evento
        if self.turn_manager.is_event_phase():
            if self.event_finished:
                # Evento já terminou, mostra confirmação
                print(f"[IA-{current_player.name}] Solicitando passar o turno...")
                self.showing_turn_confirmation = True
            else:
                # Executa evento
                print(f"[IA-{current_player.name}] Iniciando roleta de eventos...")
                self.roulette.set_player_events(current_player.name)
                self.showing_roulette = True
                self.roulette.start_spin()
                self.audio_manager.play_sound_limited(SOUND_ROULETTE, 1200)
            return
    
    def _ai_execute_attack(self):
        """IA executa um ataque"""
        current_player = self.turn_manager.get_current_player()
        
        # Escolhe continente atacante aleatório (entre os que tem presença)
        valid_attackers = [c for c in self.continents if c.get_control_percentage(current_player.name) > 0]
        
        if not valid_attackers:
            print(f"[IA-{current_player.name}] Sem continentes para atacar!")
            self.turn_manager.skip_attack_phase()
            return
        
        attacker_continent = random.choice(valid_attackers)
        
        # Escolhe alvo: próprio continente ou adjacente aleatório
        possible_targets = [attacker_continent]
        adjacent_names = ADJACENT_CONTINENTS.get(attacker_continent.name, [])
        for adj_name in adjacent_names:
            adj_continent = next((c for c in self.continents if c.name == adj_name), None)
            if adj_continent:
                possible_targets.append(adj_continent)
        
        target_continent = random.choice(possible_targets)
        
        print(f"[IA-{current_player.name}] Atacando de '{attacker_continent.name}' para '{target_continent.name}'")
        
        self.selected_attack_continent = attacker_continent
        self.selected_target_continent = target_continent
        
        # Mostra seleção de inimigo
        self.showing_enemy_selection = True
    
    def _ai_select_enemy(self):
        """IA seleciona um inimigo aleatório"""
        current_player = self.turn_manager.get_current_player()
        enemies = [p for p in self.players if p.name != current_player.name]
        
        # Escolhe inimigo aleatório
        selected_enemy = random.choice(enemies)
        
        print(f"[IA-{current_player.name}] Alvo: {selected_enemy.name}")
        
        self.audio_manager.play_sound(SOUND_CLICK)
        self.showing_enemy_selection = False
        self._prepare_combat(selected_enemy)
    
    def _ai_handle_dice_results(self):
        """IA trata resultados de dados e re-roll"""
        current_player = self.turn_manager.get_current_player()
        
        # Se é Linux e pode re-rolar, re-rola o menor dado do atacante
        if current_player.name == "Linux" and current_player.can_reroll() and self.current_attacker == current_player:
            # Encontra o menor dado
            min_index = self.attacker_dice_results.index(min(self.attacker_dice_results))
            old_value = self.attacker_dice_results[min_index]
            
            print(f"[IA-{current_player.name}] Re-rolando o menor dado ({old_value})...")
            
            self.audio_manager.play_sound(SOUND_DICE_ROLL)
            from game.utils.helpers import roll_dice
            self.attacker_dice_results[min_index] = roll_dice(1)[0]
            current_player.use_reroll()
            
            print(f"[IA-{current_player.name}] Novo valor: {self.attacker_dice_results[min_index]}")
            
            # Aguarda antes de continuar
            import time
            self.ai_action_timer = time.time()
            self.ai_waiting = True
            return
        
        # Continua para finalização do combate
        print(f"[IA-{current_player.name}] Finalizando combate...")
        self.audio_manager.play_sound(SOUND_CLICK)
        import time
        self.showing_dice_results = False
        self._finish_combat()
        self.combat_result_animation_start = time.time()
    
    # ==================================================================
    # Métodos de Reinforcement Learning
    # ==================================================================
    
    def _init_rl_agents(self):
        """Inicializa agentes RL para jogadores configurados como RL"""
        self.rl_agents = {}
        if not RL_AVAILABLE:
            print("[RL] PyTorch não disponível. Jogadores RL serão tratados como IA aleatória.")
            for player in self.players:
                if player.is_rl:
                    player.is_rl = False
                    player.is_ai = True
            return
        
        for player in self.players:
            if player.is_rl:
                try:
                    agent = RLAgent(
                        player_name=player.name,
                        training=False,  # Modo inferência no jogo
                        model_path=None  # Usa caminho padrão
                    )
                    self.rl_agents[player.name] = agent
                    print(f"[RL] Agente RL inicializado para {player.name}")
                except Exception as e:
                    print(f"[RL] Erro ao inicializar agente RL para {player.name}: {e}")
                    print(f"[RL] {player.name} será controlado por IA aleatória.")
                    player.is_rl = False
                    player.is_ai = True
    
    def _execute_rl_action(self):
        """Executa a próxima ação do agente RL baseado no estado atual"""
        current_player = self.turn_manager.get_current_player()
        agent = self.rl_agents.get(current_player.name)
        
        if not agent:
            # Fallback para IA aleatória
            self._execute_ai_action()
            return
        
        # Estados intermediários (combate, dados, roleta) são tratados como IA 
        # pois o RL decide apenas na fase de ataque (atacar/passar + parâmetros)
        
        # Se está mostrando resultado de combate, apenas avança
        if self.showing_combat_result:
            print(f"[RL-{current_player.name}] Visualizando resultado do combate...")
            self.audio_manager.play_sound(SOUND_CLICK)
            self.audio_manager.play_music(MUSIC_GAME)
            self.showing_combat_result = False
            self.combat_system.clear_last_result()
            self._check_win_condition()
            return
        
        # Se está mostrando dados, trata re-roll ou continua
        if self.showing_dice_results:
            self._rl_handle_dice_results()
            return
        
        # Se está em preparação de combate, rola os dados
        if self.preparing_combat:
            print(f"[RL-{current_player.name}] Rolando dados: {self.attacker_dice_count} atacante vs {self.defender_dice_count} defensor")
            self.audio_manager.play_sound(SOUND_CLICK)
            self._roll_dice()
            return
        
        # Se está mostrando seleção de inimigo - não deveria chegar aqui, mas safety
        if self.showing_enemy_selection:
            self._ai_select_enemy()
            return
        
        # Se está mostrando resultado de evento
        if self.showing_event_result:
            print(f"[RL-{current_player.name}] Evento aplicado!")
            self.audio_manager.play_sound(SOUND_CLICK)
            self.showing_event_result = False
            self.showing_roulette = False
            self.event_applied_continent = None
            self.event_result = None
            self.event_finished = True
            return
        
        # Se está mostrando a roleta
        if self.showing_roulette:
            if not self.roulette.is_spinning():
                print(f"[RL-{current_player.name}] Aplicando evento aleatório...")
                self._apply_random_event()
            return
        
        # Se está mostrando confirmação de passar turno
        if self.showing_turn_confirmation:
            print(f"[RL-{current_player.name}] Passando o turno...")
            self.audio_manager.play_sound(SOUND_CLICK)
            self.showing_turn_confirmation = False
            self.event_finished = False
            self._next_turn()
            return
        
        # Fase de ataque - decisão do RL
        if self.turn_manager.is_attack_phase():
            if self.turn_manager.can_attack():
                self._rl_decide_attack()
            else:
                # Sem ataques, passa para fase de evento
                print(f"[RL-{current_player.name}] Sem mais ataques. Passando para fase de evento...")
                self.audio_manager.play_sound(SOUND_CLICK)
                self.turn_manager.skip_attack_phase()
                self.selected_attack_continent = None
            return
        
        # Fase de evento
        if self.turn_manager.is_event_phase():
            if self.event_finished:
                print(f"[RL-{current_player.name}] Solicitando passar o turno...")
                self.showing_turn_confirmation = True
            else:
                print(f"[RL-{current_player.name}] Iniciando roleta de eventos...")
                self.roulette.set_player_events(current_player.name)
                self.showing_roulette = True
                self.roulette.start_spin()
                self.audio_manager.play_sound_limited(SOUND_ROULETTE, 1200)
            return
    
    def _rl_decide_attack(self):
        """RL decide se ataca e como ataca"""
        current_player = self.turn_manager.get_current_player()
        agent = self.rl_agents.get(current_player.name)
        
        if not agent:
            self._ai_execute_attack()
            return
        
        from game.utils.constants import MIN_DICE
        
        # Obtém estado
        state = agent.get_state(
            self.continents, current_player.name,
            self.turn_manager.attacks_remaining,
            self.turn_manager.is_attack_phase()
        )
        
        # Obtém inimigos
        enemies = [p.name for p in self.players if p.name != current_player.name]
        
        # Máscara de ações válidas
        valid_mask = agent.get_valid_actions_mask(
            self.continents, current_player.name, enemies,
            self.turn_manager.attacks_remaining,
            self.turn_manager.is_attack_phase()
        )
        
        # Seleciona ação
        action_idx = agent.select_action(state, valid_mask)
        action = agent.decode_action(action_idx, self.continents, 
                                      [p for p in self.players if p.name != current_player.name],
                                      current_player.name)
        
        if action["type"] == "pass":
            # Passa fase de ataque
            print(f"[RL-{current_player.name}] Decidiu passar a fase de ataque")
            self.audio_manager.play_sound(SOUND_CLICK)
            self.turn_manager.skip_attack_phase()
            self.selected_attack_continent = None
            return
        
        # Executa ataque
        src = action["source_continent"]
        tgt = action["target_continent"]
        enemy = action["enemy"]
        dice_level = action["dice_level"]
        
        print(f"[RL-{current_player.name}] Ataca de '{src.name}' para '{tgt.name}' contra {enemy.name} (dados: nível {dice_level})")
        
        self.selected_attack_continent = src
        self.selected_target_continent = tgt
        
        # Prepara combate diretamente (pula seleção de inimigo visual)
        self.showing_enemy_selection = False
        self._prepare_combat(enemy)
        
        # Ajusta dados baseado no nível escolhido pelo RL
        if dice_level == 0:
            self.attacker_dice_count = MIN_DICE
        elif dice_level == 1:
            self.attacker_dice_count = max(MIN_DICE, self.max_attacker_dice // 2)
        else:
            self.attacker_dice_count = self.max_attacker_dice
    
    def _rl_handle_dice_results(self):
        """RL trata resultados de dados e re-roll"""
        current_player = self.turn_manager.get_current_player()
        
        # Se é Linux e pode re-rolar, re-rola o menor dado
        if current_player.name == "Linux" and current_player.can_reroll() and self.current_attacker == current_player:
            min_index = self.attacker_dice_results.index(min(self.attacker_dice_results))
            old_value = self.attacker_dice_results[min_index]
            
            print(f"[RL-{current_player.name}] Re-rolando o menor dado ({old_value})...")
            
            self.audio_manager.play_sound(SOUND_DICE_ROLL)
            from game.utils.helpers import roll_dice
            self.attacker_dice_results[min_index] = roll_dice(1)[0]
            current_player.use_reroll()
            
            print(f"[RL-{current_player.name}] Novo valor: {self.attacker_dice_results[min_index]}")
            
            import time
            self.ai_action_timer = time.time()
            self.ai_waiting = True
            return
        
        # Continua para finalização do combate
        print(f"[RL-{current_player.name}] Finalizando combate...")
        self.audio_manager.play_sound(SOUND_CLICK)
        import time
        self.showing_dice_results = False
        self._finish_combat()
        self.combat_result_animation_start = time.time()
    
    def _handle_mouse_motion(self, pos):
        """Trata movimento do mouse"""
        # Ignora hover durante turnos de IA ou RL
        if not self.showing_main_menu:
            current_player = self.turn_manager.get_current_player()
            if current_player.is_ai or current_player.is_rl:
                return
        
        # Ignora hover durante animação de dados
        if self.showing_dice_animation:
            return
        
        # Atualiza hover do botão
        self.ui_manager.update_button_hover(pos)
        
        # Atualiza continente sob o mouse
        if not self.showing_roulette and not self.showing_combat_result:
            self.hovered_continent = self.map_renderer.get_continent_at_position(pos)
    
    def _update(self):
        """Atualiza estado do jogo"""
        import time
        
        # Atualiza roleta se estiver girando
        if self.showing_roulette and self.roulette.is_spinning():
            self.roulette.update()
        
        # IA/RL: executa ações automaticamente
        if not self.showing_main_menu and not self.game_over:
            current_player = self.turn_manager.get_current_player()
            is_automated = current_player.is_ai or current_player.is_rl
            
            if is_automated and not self.ai_waiting:
                # Inicia timer de ação
                self.ai_waiting = True
                self.ai_action_timer = time.time()
            
            if is_automated and self.ai_waiting:
                # Espera o delay antes de executar a próxima ação
                if time.time() - self.ai_action_timer >= self.ai_action_delay:
                    self.ai_waiting = False
                    if current_player.is_rl:
                        self._execute_rl_action()
                    else:
                        self._execute_ai_action()
    
    def _render(self):
        """Renderiza o jogo"""
        # Fundo
        self.screen.fill(OCEAN_BLUE)
        
        # Se está mostrando menu principal
        if self.showing_main_menu:
            # Renderiza o mapa primeiro para usar como fundo
            self.map_renderer.render(None)
            # Cria uma cópia da tela atual para passar como fundo
            map_surface = self.screen.copy()
            # Limpa a tela novamente
            self.screen.fill(OCEAN_BLUE)
            # Renderiza o menu com o mapa como fundo
            self.ui_manager.render_main_menu(map_surface)
            pygame.display.flip()
            return
        
        # Mapa
        highlight = self.selected_attack_continent if self.selected_attack_continent else self.hovered_continent
        self.map_renderer.render(highlight)
        
        current_player = self.turn_manager.get_current_player()
        player_color = PLAYER_COLORS[current_player.name]
        
        # Destaque do continente selecionado para ataque (com cor do jogador)
        if self.selected_attack_continent and not self.showing_combat_result:
            rect = self.selected_attack_continent.rect
            pygame.draw.rect(self.screen, player_color, rect, 4)
        
        # Desenha setas animadas se há um continente selecionado e um sob o mouse
        if (self.selected_attack_continent and self.hovered_continent and 
            not self.showing_combat_result and 
            self.hovered_continent != self.selected_attack_continent and
            self._can_attack(self.selected_attack_continent, self.hovered_continent)):
            self._draw_attack_arrows(
                self.selected_attack_continent, 
                self.hovered_continent, 
                player_color
            )
        
        # Painel inferior (sempre visível)
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
            event_finished=self.event_finished,
            selected_attack_continent=self.selected_attack_continent
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
        
        # Preparação de combate
        if self.preparing_combat:
            current_player = self.turn_manager.get_current_player()
            self.ui_manager.render_combat_preparation(
                current_player,
                self.selected_enemy,
                self.attacker_dice_count,
                self.defender_dice_count,
                self.max_attacker_dice,
                self.max_defender_dice,
                self.logos
            )
        
        # Animação de dados
        if self.showing_dice_animation:
            import time
            elapsed = time.time() - self.dice_animation_start
            self.ui_manager.render_dice_animation(
                self.current_attacker,
                self.current_defender,
                self.attacker_dice_count,
                self.defender_dice_count,
                elapsed,
                self.logos
            )
        
        # Resultados dos dados (com opção de re-roll)
        if self.showing_dice_results:
            self.ui_manager.render_dice_results(
                self.current_attacker,
                self.current_defender,
                self.attacker_dice_results,
                self.defender_dice_results,
                self.logos
            )
        
        # Resultado de combate
        if self.showing_combat_result:
            import time
            animation_elapsed = time.time() - self.combat_result_animation_start
            
            # Toca som de machine gun durante a animação (2 vezes) se houve conquista
            result = self.combat_system.last_combat_result
            if result and result["attacker_wins"] > 0:
                # Primeira vez no início da animação
                if animation_elapsed >= 0.5 and self.machine_gun_count == 0:
                    self.audio_manager.play_sound(SOUND_CONQUEST)
                    self.machine_gun_count = 1
                # Segunda vez após 1.2 segundos
                elif animation_elapsed >= 1.2 and self.machine_gun_count == 1:
                    self.audio_manager.play_sound(SOUND_CONQUEST)
                    self.machine_gun_count = 2
            
            self.ui_manager.render_combat_result(
                self.combat_system.last_combat_result,
                animation_elapsed,
                self.combat_result_animation_duration
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
        
        # Confirmação de passar turno
        if self.showing_turn_confirmation:
            self.ui_manager.render_turn_confirmation()
        
        # Atualiza tela
        pygame.display.flip()
