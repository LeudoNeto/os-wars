"""
Ambiente de treinamento (headless) para o agente RL.

Simula o jogo sem interface gráfica para treinamento rápido.
Roda os turnos dos 3 jogadores, onde o agente RL controla um deles
e os outros são controlados por IA aleatória ou por outros agentes RL (self-play).
"""

import random
import copy
import numpy as np

from game.utils.constants import (
    CONTINENTS, PLAYERS, ADJACENT_CONTINENTS, WIN_PERCENTAGE,
    CONTROL_PERCENTAGE_PER_WIN, PHASE_ATTACK, PHASE_EVENT
)
from game.utils.helpers import (
    distribute_initial_control, calculate_dice_count, roll_dice,
    resolve_combat, apply_combat_result, apply_event, normalize_percentages
)
from game.models.event import get_random_event
from game.rl.rl_agent import RLAgent, ACTION_SPACE, NUM_ACTIONS


class HeadlessContinent:
    """Continente simplificado (sem pygame) para treinamento"""
    
    def __init__(self, name):
        self.name = name
        self.control = {}
    
    def get_control_percentage(self, player):
        return self.control.get(player, 0)
    
    def get_controller(self):
        if not self.control:
            return None
        return max(self.control.items(), key=lambda x: x[1])[0]
    
    def is_adjacent_to(self, other):
        return other.name in ADJACENT_CONTINENTS.get(self.name, [])


class OSWarsEnv:
    """
    Ambiente de treinamento headless para OS Wars.
    
    Simula o jogo completo sem interface gráfica.
    O agente RL controla um jogador específico; os outros usam IA aleatória
    ou outros agentes RL (self-play).
    """
    
    def __init__(self, rl_player_name="Linux", max_turns=200, opponent_agents=None):
        """
        Args:
            rl_player_name: Nome do jogador controlado pelo RL principal
            max_turns: Número máximo de turnos antes de terminar o episódio
            opponent_agents: Dict {player_name: RLAgent} para oponentes RL (self-play).
                            Jogadores não listados usam IA aleatória.
        """
        self.rl_player_name = rl_player_name
        self.max_turns = max_turns
        self.opponent_agents = opponent_agents or {}
        self.continents = []
        self.turn_count = 0
        self.current_player_idx = 0
        self.current_phase = PHASE_ATTACK
        self.attacks_remaining = 0
        self.game_over = False
        self.winner = None
        
    def reset(self):
        """
        Reinicia o ambiente para um novo episódio.
        
        Returns:
            state: Vetor de estado inicial
        """
        # Cria continentes
        self.continents = [HeadlessContinent(name) for name in CONTINENTS]
        
        # Distribui controle inicial
        initial_control = distribute_initial_control()
        for continent in self.continents:
            continent.control = initial_control[continent.name].copy()
        
        # Estado do jogo
        self.turn_count = 0
        self.current_player_idx = 0
        self.current_phase = PHASE_ATTACK
        self.game_over = False
        self.winner = None
        
        # Calcula ataques para o primeiro jogador
        self._start_turn()
        
        # Avança até que seja a vez do RL na fase de ataque
        self._advance_to_rl_turn()
        
        return self._get_state()
    
    def _start_turn(self):
        """Inicia turno do jogador atual"""
        player_name = PLAYERS[self.current_player_idx]
        # Número de ataques = continentes controlados (min 1)
        controlled = sum(1 for c in self.continents if c.get_controller() == player_name)
        self.attacks_remaining = max(1, controlled)
        self.current_phase = PHASE_ATTACK
    
    def _get_current_player(self):
        return PLAYERS[self.current_player_idx]
    
    def _get_state(self):
        """Retorna vetor de estado para o agente RL"""
        state = []
        
        # Porcentagens (18 valores)
        for continent in self.continents:
            for player in PLAYERS:
                state.append(continent.get_control_percentage(player) / 100.0)
        
        # Controle total médio (3 valores)
        for player in PLAYERS:
            total = sum(c.get_control_percentage(player) for c in self.continents)
            state.append(total / (len(self.continents) * 100.0))
        
        # Ataques restantes (1 valor)
        state.append(min(self.attacks_remaining / 6.0, 1.0))
        
        # Fase (1 valor)
        state.append(0.0 if self.current_phase == PHASE_ATTACK else 1.0)
        
        return np.array(state, dtype=np.float32)
    
    def _get_valid_mask(self):
        """Retorna máscara de ações válidas"""
        player_name = self.rl_player_name
        enemies = [p for p in PLAYERS if p != player_name]
        
        mask = np.zeros(NUM_ACTIONS, dtype=bool)
        mask[0] = True  # Passar sempre válido
        
        if self.current_phase != PHASE_ATTACK or self.attacks_remaining <= 0:
            return mask
        
        for i, action in enumerate(ACTION_SPACE):
            if action["type"] == "pass":
                continue
            
            src_idx = action["source_idx"]
            tgt_idx = action["target_idx"]
            enemy_idx = action["enemy_idx"]
            
            if enemy_idx >= len(enemies):
                continue
            
            src = self.continents[src_idx]
            tgt = self.continents[tgt_idx]
            
            if src.get_control_percentage(player_name) <= 0:
                continue
            
            if src_idx != tgt_idx and not src.is_adjacent_to(tgt):
                continue
            
            enemy_name = enemies[enemy_idx]
            if tgt.get_control_percentage(enemy_name) <= 0:
                continue
            
            mask[i] = True
        
        return mask
    
    def _get_valid_mask_for_player(self, player_name):
        """Retorna máscara de ações válidas para um jogador específico"""
        enemies = [p for p in PLAYERS if p != player_name]
        
        mask = np.zeros(NUM_ACTIONS, dtype=bool)
        mask[0] = True
        
        if self.current_phase != PHASE_ATTACK or self.attacks_remaining <= 0:
            return mask
        
        for i, action in enumerate(ACTION_SPACE):
            if action["type"] == "pass":
                continue
            
            src_idx = action["source_idx"]
            tgt_idx = action["target_idx"]
            enemy_idx = action["enemy_idx"]
            
            if enemy_idx >= len(enemies):
                continue
            
            src = self.continents[src_idx]
            tgt = self.continents[tgt_idx]
            
            if src.get_control_percentage(player_name) <= 0:
                continue
            
            if src_idx != tgt_idx and not src.is_adjacent_to(tgt):
                continue
            
            enemy_name = enemies[enemy_idx]
            if tgt.get_control_percentage(enemy_name) <= 0:
                continue
            
            mask[i] = True
        
        return mask
    
    def _get_state_for_player(self, player_name):
        """Retorna vetor de estado para um jogador específico"""
        state = []
        for continent in self.continents:
            for player in PLAYERS:
                state.append(continent.get_control_percentage(player) / 100.0)
        for player in PLAYERS:
            total = sum(c.get_control_percentage(player) for c in self.continents)
            state.append(total / (len(self.continents) * 100.0))
        state.append(min(self.attacks_remaining / 6.0, 1.0))
        state.append(0.0 if self.current_phase == PHASE_ATTACK else 1.0)
        return np.array(state, dtype=np.float32)
    
    def step(self, action_idx):
        """
        Executa uma ação do agente RL.
        
        Args:
            action_idx: Índice da ação no espaço de ações
        
        Returns:
            next_state, reward, done, info
        """
        # Snapshot antes da ação
        control_before = {
            c.name: dict(c.control) for c in self.continents
        }
        
        action_def = ACTION_SPACE[action_idx]
        player_name = self.rl_player_name
        enemies = [p for p in PLAYERS if p != player_name]
        
        if action_def["type"] == "pass":
            # Passa fase de ataque → executa evento → próximo turno
            self._execute_event(player_name)
            self._next_turn()
            # Avança turnos dos outros jogadores
            self._advance_to_rl_turn()
        else:
            # Executa ataque
            src = self.continents[action_def["source_idx"]]
            tgt = self.continents[action_def["target_idx"]]
            enemy_name = enemies[action_def["enemy_idx"]]
            dice_level = action_def["dice_level"]
            
            self._execute_attack(player_name, enemy_name, src, tgt, dice_level)
            self.attacks_remaining -= 1
            
            # Se não tem mais ataques, passa para evento
            if self.attacks_remaining <= 0:
                self._execute_event(player_name)
                self._next_turn()
                self._advance_to_rl_turn()
        
        # Verifica vitória
        self._check_win_condition()
        
        # Verifica limite de turnos
        done = self.game_over or self.turn_count >= self.max_turns
        
        # Calcula recompensa
        reward = RLAgent.calculate_reward(
            self.continents, player_name, control_before,
            game_over=self.game_over, winner_name=self.winner
        )
        
        # Se atingiu limite de turnos sem vencer, penalidade leve
        if self.turn_count >= self.max_turns and not self.game_over:
            reward -= 5.0
            done = True
        
        next_state = self._get_state()
        info = {
            "turn": self.turn_count,
            "winner": self.winner,
            "game_over": self.game_over,
            "action_type": action_def["type"]
        }
        
        return next_state, reward, done, info
    
    def _execute_attack(self, attacker_name, defender_name, src, tgt, dice_level):
        """Executa um ataque no ambiente headless"""
        # Calcula dados
        attacker_control = src.get_control_percentage(attacker_name)
        defender_control = tgt.get_control_percentage(defender_name)
        
        # Bônus do atacante
        attack_bonus = 1 if attacker_name == "Windows" else 0
        max_attacker_dice = calculate_dice_count(attacker_control, bonus=attack_bonus)
        max_defender_dice = calculate_dice_count(defender_control)
        
        # Nível de dados
        if dice_level == 0:
            attacker_dice_count = 1
        elif dice_level == 1:
            attacker_dice_count = max(1, max_attacker_dice // 2)
        else:
            attacker_dice_count = max_attacker_dice
        
        defender_dice_count = max_defender_dice
        
        # Rola dados
        attacker_dice = roll_dice(attacker_dice_count)
        defender_dice = roll_dice(defender_dice_count)
        
        # Bônus de defesa MacOS
        if defender_name == "MacOS":
            defender_dice = [d + 1 for d in defender_dice]
        
        # Habilidade Linux: re-rola menor dado
        if attacker_name == "Linux" and len(attacker_dice) > 0:
            min_idx = attacker_dice.index(min(attacker_dice))
            attacker_dice[min_idx] = roll_dice(1)[0]
        
        # Resolve combate
        wins = resolve_combat(attacker_dice, defender_dice)
        
        # Aplica resultado
        apply_combat_result(tgt.control, attacker_name, defender_name, wins)
    
    def _execute_event(self, player_name):
        """Executa fase de evento aleatório"""
        event = get_random_event(player_name)
        continent = random.choice(self.continents)
        apply_event(continent.control, player_name, event.percentage)
    
    def _next_turn(self):
        """Avança para o próximo jogador"""
        self.current_player_idx = (self.current_player_idx + 1) % len(PLAYERS)
        self._start_turn()
        self.turn_count += 1
    
    def _advance_to_rl_turn(self):
        """
        Executa turnos de jogadores não-RL até que seja a vez do jogador RL.
        Jogadores com agente RL em opponent_agents usam essa rede; os demais usam IA aleatória.
        """
        max_iterations = len(PLAYERS) * 2
        iterations = 0
        
        while self._get_current_player() != self.rl_player_name and iterations < max_iterations:
            current = self._get_current_player()
            
            if current in self.opponent_agents:
                self._execute_rl_opponent_turn(current)
            else:
                self._execute_random_ai_turn()
            
            self._check_win_condition()
            if self.game_over:
                return
            self._next_turn()
            iterations += 1
    
    def _execute_rl_opponent_turn(self, player_name):
        """Executa turno de um oponente controlado por RL"""
        agent = self.opponent_agents[player_name]
        enemies = [p for p in PLAYERS if p != player_name]
        
        # Fase de ataque
        for _ in range(self.attacks_remaining):
            state = self._get_state_for_player(player_name)
            valid_mask = self._get_valid_mask_for_player(player_name)
            
            # Se só pode passar, sai
            if valid_mask.sum() <= 1:
                break
            
            action_idx = agent.select_action(state, valid_mask)
            action_def = ACTION_SPACE[action_idx]
            
            if action_def["type"] == "pass":
                break
            
            src = self.continents[action_def["source_idx"]]
            tgt = self.continents[action_def["target_idx"]]
            
            if action_def["enemy_idx"] < len(enemies):
                enemy_name = enemies[action_def["enemy_idx"]]
                if tgt.get_control_percentage(enemy_name) > 0:
                    self._execute_attack(player_name, enemy_name, src, tgt, action_def["dice_level"])
            
            self.attacks_remaining -= 1
            if self.attacks_remaining <= 0:
                break
        
        # Fase de evento
        self._execute_event(player_name)
    
    def _execute_random_ai_turn(self):
        """Executa um turno completo de IA aleatória"""
        player_name = self._get_current_player()
        enemies = [p for p in PLAYERS if p != player_name]
        
        # Fase de ataque
        for _ in range(self.attacks_remaining):
            # Escolhe continente de origem aleatório
            valid_sources = [c for c in self.continents 
                           if c.get_control_percentage(player_name) > 0]
            if not valid_sources:
                break
            
            src = random.choice(valid_sources)
            
            # Escolhe alvo: mesmo ou adjacente
            targets = [src]
            for adj_name in ADJACENT_CONTINENTS.get(src.name, []):
                adj = next((c for c in self.continents if c.name == adj_name), None)
                if adj:
                    targets.append(adj)
            
            tgt = random.choice(targets)
            
            # Escolhe inimigo aleatório que tenha presença no alvo
            valid_enemies = [e for e in enemies if tgt.get_control_percentage(e) > 0]
            if not valid_enemies:
                continue
            
            enemy = random.choice(valid_enemies)
            
            # Executa ataque com dados máximos
            self._execute_attack(player_name, enemy, src, tgt, dice_level=2)
        
        # Fase de evento
        self._execute_event(player_name)
    
    def _check_win_condition(self):
        """Verifica se algum jogador venceu"""
        for player in PLAYERS:
            all_controlled = all(
                c.get_control_percentage(player) >= WIN_PERCENTAGE
                for c in self.continents
            )
            if all_controlled:
                self.game_over = True
                self.winner = player
                return
    
    def get_valid_actions(self):
        """Retorna máscara de ações válidas (para uso externo)"""
        return self._get_valid_mask()
