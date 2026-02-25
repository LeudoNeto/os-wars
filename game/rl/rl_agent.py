"""
Agente de Reinforcement Learning (DQN) para OS Wars.

O agente decide:
  1. Atacar ou passar a fase de ataque
  2. Qual continente usar como origem
  3. Qual continente alvo
  4. Qual inimigo atacar
  5. Quantos dados usar (atacante)

Observação (state):
  - 18 valores: porcentagem de cada jogador em cada continente (6 cont × 3 jogadores)
  - 3 valores: controle total médio de cada jogador
  - 1 valor: ataques restantes (normalizado)
  - 1 valor: fase atual (0 = ataque, 1 = evento)
  Total: 23 dimensões

Ações:
  Ação 0: Passar fase (não atacar / passar turno)
  Ações 1..N: Combinações de (continente_origem, continente_alvo, inimigo, dados)
  
  Para simplificar, usamos um espaço de ações hierárquico achatado:
  - 6 origens × 7 alvos (mesmo + 6 adjacentes max) × 2 inimigos × 3 níveis de dados = ~252 ações possíveis
  Mas como a adjacência é fixa, pré-calculamos todas as 
  combinações válidas + ação de "passar".
"""

import numpy as np
import random
import os
import json
from collections import deque

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("[RL] PyTorch não encontrado. Instale com: pip install torch")

from game.utils.constants import CONTINENTS, PLAYERS, ADJACENT_CONTINENTS


# ============================================================
# Definição do espaço de ações
# ============================================================

def build_action_space():
    """
    Constrói o espaço de ações possíveis.
    
    Cada ação é um dicionário:
      - type: "pass" ou "attack"
      - source_idx: índice do continente de origem (0-5)
      - target_idx: índice do continente alvo (0-5)
      - enemy_idx: índice do inimigo (0 ou 1, relativo à lista de inimigos)
      - dice_level: 0=mínimo, 1=metade, 2=máximo
    
    Retorna: lista de dicts descrevendo cada ação
    """
    actions = []
    
    # Ação 0: passar fase
    actions.append({"type": "pass"})
    
    # Ações de ataque
    for src_idx, src_name in enumerate(CONTINENTS):
        # Alvos possíveis: o próprio continente + adjacentes
        targets = [src_name] + ADJACENT_CONTINENTS.get(src_name, [])
        for tgt_name in targets:
            tgt_idx = CONTINENTS.index(tgt_name)
            for enemy_idx in range(2):  # 2 inimigos possíveis
                for dice_level in range(3):  # min, metade, máximo
                    actions.append({
                        "type": "attack",
                        "source_idx": src_idx,
                        "target_idx": tgt_idx,
                        "enemy_idx": enemy_idx,
                        "dice_level": dice_level
                    })
    
    return actions


ACTION_SPACE = build_action_space()
NUM_ACTIONS = len(ACTION_SPACE)
STATE_DIM = 23  # 18 controles + 3 totais + 1 ataques restantes + 1 fase


# ============================================================
# Rede Neural (DQN)
# ============================================================

if TORCH_AVAILABLE:
    class DQNNetwork(nn.Module):
        """Rede neural Deep Q-Network"""
        
        def __init__(self, state_dim, action_dim, hidden_dim=256):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(state_dim, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, hidden_dim // 2),
                nn.ReLU(),
                nn.Linear(hidden_dim // 2, action_dim)
            )
        
        def forward(self, x):
            return self.net(x)


# ============================================================
# Replay Buffer
# ============================================================

class ReplayBuffer:
    """Buffer de experiências para treinamento"""
    
    def __init__(self, capacity=200000):
        self.buffer = deque(maxlen=capacity)
    
    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))
    
    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        return (
            np.array(states, dtype=np.float32),
            np.array(actions, dtype=np.int64),
            np.array(rewards, dtype=np.float32),
            np.array(next_states, dtype=np.float32),
            np.array(dones, dtype=np.float32)
        )
    
    def __len__(self):
        return len(self.buffer)


# ============================================================
# Agente RL
# ============================================================

class RLAgent:
    """
    Agente de Reinforcement Learning usando DQN.
    
    Pode operar em modo de treinamento (com exploração) ou 
    modo de inferência (greedy).
    """
    
    def __init__(self, player_name, training=False, model_path=None,
                 lr=1e-4, gamma=0.99, epsilon_start=1.0, epsilon_end=0.05,
                 epsilon_decay=0.9995, batch_size=64, target_update=1000):
        """
        Args:
            player_name: Nome do jogador ("Windows", "MacOS" ou "Linux")
            training: Se está em modo de treinamento
            model_path: Caminho para carregar/salvar modelo
            lr: Taxa de aprendizado
            gamma: Fator de desconto
            epsilon_start: Epsilon inicial (exploração)
            epsilon_end: Epsilon final
            epsilon_decay: Taxa de decaimento do epsilon
            batch_size: Tamanho do batch de treinamento
            target_update: Frequência de atualização da rede alvo (em passos)
        """
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch é necessário para o agente RL. Instale com: pip install torch")
        
        self.player_name = player_name
        self.training = training
        self.gamma = gamma
        self.batch_size = batch_size
        self.target_update_freq = target_update
        
        # Epsilon-greedy
        self.epsilon = epsilon_start if training else 0.0
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        
        # Redes
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.policy_net = DQNNetwork(STATE_DIM, NUM_ACTIONS).to(self.device)
        self.target_net = DQNNetwork(STATE_DIM, NUM_ACTIONS).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        
        # Otimizador
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=lr)
        
        # Buffer de replay
        self.replay_buffer = ReplayBuffer()
        
        # Contadores
        self.steps_done = 0
        self.episodes_done = 0
        
        # Estado anterior (para calcular recompensa)
        self.last_state = None
        self.last_action = None
        self.cumulative_reward = 0.0
        
        # Métricas de treinamento
        self.episode_rewards = []
        self.losses = []
        
        # Caminho do modelo
        self.model_path = model_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "models", f"rl_agent_{player_name.lower()}.pth"
        )
        
        # Tenta carregar modelo existente
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        elif not training and os.path.exists(self.model_path):
            self.load_model(self.model_path)
    
    # ----------------------------------------------------------
    # Estado
    # ----------------------------------------------------------
    
    def get_state(self, continents, player_name, attacks_remaining, is_attack_phase):
        """
        Converte o estado do jogo em vetor numérico.
        
        Args:
            continents: Lista de objetos Continent
            player_name: Nome do jogador atual
            attacks_remaining: Ataques restantes
            is_attack_phase: Se está na fase de ataque
        
        Returns:
            np.array com o estado normalizado (23 dims)
        """
        state = []
        
        # Porcentagens de controle (18 valores, normalizados 0-1)
        for continent in continents:
            for player in PLAYERS:
                state.append(continent.get_control_percentage(player) / 100.0)
        
        # Controle total médio de cada jogador (3 valores, 0-1)
        for player in PLAYERS:
            total = sum(c.get_control_percentage(player) for c in continents) / len(continents)
            state.append(total / 100.0)
        
        # Ataques restantes (normalizado, assume max 6)
        state.append(min(attacks_remaining / 6.0, 1.0))
        
        # Fase (0=ataque, 1=evento)
        state.append(0.0 if is_attack_phase else 1.0)
        
        return np.array(state, dtype=np.float32)
    
    # ----------------------------------------------------------
    # Máscara de ações válidas
    # ----------------------------------------------------------
    
    def get_valid_actions_mask(self, continents, player_name, enemies, 
                                attacks_remaining, is_attack_phase):
        """
        Retorna uma máscara booleana indicando quais ações são válidas.
        
        Args:
            continents: Lista de objetos Continent
            player_name: Nome do jogador
            enemies: Lista de nomes dos inimigos
            attacks_remaining: Ataques restantes
            is_attack_phase: Se está na fase de ataque
        
        Returns:
            np.array booleano de tamanho NUM_ACTIONS
        """
        mask = np.zeros(NUM_ACTIONS, dtype=bool)
        
        # Ação 0: passar sempre é válida
        mask[0] = True
        
        if not is_attack_phase or attacks_remaining <= 0:
            return mask
        
        # Para cada ação de ataque, verifica validade
        for i, action in enumerate(ACTION_SPACE):
            if action["type"] == "pass":
                continue
            
            src_idx = action["source_idx"]
            tgt_idx = action["target_idx"]
            enemy_idx = action["enemy_idx"]
            
            # Verifica se o inimigo existe
            if enemy_idx >= len(enemies):
                continue
            
            src_continent = continents[src_idx]
            tgt_continent = continents[tgt_idx]
            
            # Verifica se o jogador tem presença no continente de origem
            if src_continent.get_control_percentage(player_name) <= 0:
                continue
            
            # Verifica adjacência ou mesmo continente
            if src_idx != tgt_idx and not src_continent.is_adjacent_to(tgt_continent):
                continue
            
            # Verifica se o inimigo tem presença no continente alvo
            enemy_name = enemies[enemy_idx]
            if tgt_continent.get_control_percentage(enemy_name) <= 0:
                continue
            
            mask[i] = True
        
        return mask
    
    # ----------------------------------------------------------
    # Seleção de ação
    # ----------------------------------------------------------
    
    def select_action(self, state, valid_mask):
        """
        Seleciona uma ação usando epsilon-greedy.
        
        Args:
            state: Vetor de estado
            valid_mask: Máscara de ações válidas
        
        Returns:
            Índice da ação escolhida
        """
        valid_indices = np.where(valid_mask)[0]
        
        if len(valid_indices) == 0:
            return 0  # Passa se não há ação válida
        
        # Exploração
        if self.training and random.random() < self.epsilon:
            action = np.random.choice(valid_indices)
        else:
            # Exploitação (greedy)
            with torch.no_grad():
                state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
                q_values = self.policy_net(state_tensor).squeeze(0).cpu().numpy()
                
                # Mascara ações inválidas com -inf
                masked_q = np.full(NUM_ACTIONS, -np.inf)
                masked_q[valid_indices] = q_values[valid_indices]
                
                action = int(np.argmax(masked_q))
        
        return action
    
    # ----------------------------------------------------------
    # Decodificação de ação
    # ----------------------------------------------------------
    
    def decode_action(self, action_idx, continents, enemies, player_name):
        """
        Decodifica um índice de ação para parâmetros do jogo.
        
        Returns:
            dict com os parâmetros da ação, ou None se for "pass"
        """
        action_def = ACTION_SPACE[action_idx]
        
        if action_def["type"] == "pass":
            return {"type": "pass"}
        
        src_continent = continents[action_def["source_idx"]]
        tgt_continent = continents[action_def["target_idx"]]
        enemy = enemies[action_def["enemy_idx"]]
        dice_level = action_def["dice_level"]
        
        return {
            "type": "attack",
            "source_continent": src_continent,
            "target_continent": tgt_continent,
            "enemy": enemy,
            "dice_level": dice_level  # 0=min, 1=metade, 2=max
        }
    
    # ----------------------------------------------------------
    # Recompensas
    # ----------------------------------------------------------
    
    @staticmethod
    def calculate_reward(continents, player_name, control_before, 
                         game_over=False, winner_name=None):
        """
        Calcula a recompensa baseada na variação do estado.
        
        Componentes da recompensa:
          1. Variação de controle total (+/- proporcional)
          2. Bônus por manter/conquistar maioria em continentes
          3. Grande bônus/penalidade por vitória/derrota
          4. Pequena penalidade por turno (incentiva eficiência)
        
        Args:
            continents: Lista de Continent (estado atual)
            player_name: Nome do jogador RL
            control_before: Dict {continent_name: {player: %}} antes da ação
            game_over: Se o jogo acabou
            winner_name: Nome do vencedor (se game_over)
        
        Returns:
            float: recompensa
        """
        reward = 0.0
        
        # 1. Variação de controle total
        total_before = 0.0
        total_after = 0.0
        for continent in continents:
            total_before += control_before[continent.name].get(player_name, 0)
            total_after += continent.get_control_percentage(player_name)
        
        control_delta = (total_after - total_before) / 100.0  # Normalizado
        reward += control_delta * 5.0  # Peso de 5 por ponto percentual
        
        # 2. Bônus por maioria em continentes
        continents_controlled_before = 0
        continents_controlled_after = 0
        from game.utils.constants import WIN_PERCENTAGE
        
        for continent in continents:
            before_pct = control_before[continent.name].get(player_name, 0)
            after_pct = continent.get_control_percentage(player_name)
            
            if before_pct >= WIN_PERCENTAGE:
                continents_controlled_before += 1
            if after_pct >= WIN_PERCENTAGE:
                continents_controlled_after += 1
        
        # Bônus por conquistar maioria em novo continente
        new_majorities = continents_controlled_after - continents_controlled_before
        reward += new_majorities * 3.0
        
        # Bônus incremental por cada continente controlado
        reward += continents_controlled_after * 0.1
        
        # 3. Vitória / Derrota
        if game_over:
            if winner_name == player_name:
                reward += 50.0  # Grande recompensa por vencer
            else:
                reward -= 30.0  # Penalidade por perder
        
        # 4. Pequena penalidade por turno (incentiva ação eficiente)
        reward -= 0.01
        
        return reward
    
    # ----------------------------------------------------------
    # Treinamento
    # ----------------------------------------------------------
    
    def store_transition(self, state, action, reward, next_state, done):
        """Armazena uma transição no replay buffer"""
        self.replay_buffer.push(state, action, reward, next_state, done)
    
    def train_step(self):
        """
        Executa um passo de treinamento (atualização da rede).
        
        Returns:
            float: loss do passo, ou None se buffer insuficiente
        """
        if len(self.replay_buffer) < self.batch_size:
            return None
        
        states, actions, rewards, next_states, dones = self.replay_buffer.sample(self.batch_size)
        
        states_t = torch.FloatTensor(states).to(self.device)
        actions_t = torch.LongTensor(actions).to(self.device)
        rewards_t = torch.FloatTensor(rewards).to(self.device)
        next_states_t = torch.FloatTensor(next_states).to(self.device)
        dones_t = torch.FloatTensor(dones).to(self.device)
        
        # Q-values atuais
        q_values = self.policy_net(states_t).gather(1, actions_t.unsqueeze(1)).squeeze(1)
        
        # Q-values alvo (Double DQN: usa policy para selecionar, target para avaliar)
        with torch.no_grad():
            next_actions = self.policy_net(next_states_t).argmax(dim=1)
            next_q_values = self.target_net(next_states_t).gather(1, next_actions.unsqueeze(1)).squeeze(1)
            target_q_values = rewards_t + self.gamma * next_q_values * (1 - dones_t)
        
        # Loss
        loss = nn.SmoothL1Loss()(q_values, target_q_values)
        
        # Backprop
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), 10.0)
        self.optimizer.step()
        
        # Atualiza rede alvo
        self.steps_done += 1
        if self.steps_done % self.target_update_freq == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())
        
        # Decay do epsilon
        if self.training:
            self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)
        
        loss_val = loss.item()
        self.losses.append(loss_val)
        return loss_val
    
    def end_episode(self, total_reward):
        """Registra o fim de um episódio"""
        self.episodes_done += 1
        self.episode_rewards.append(total_reward)
    
    # ----------------------------------------------------------
    # Salvar / Carregar
    # ----------------------------------------------------------
    
    def save_model(self, path=None):
        """Salva o modelo treinado"""
        path = path or self.model_path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        checkpoint = {
            "policy_net": self.policy_net.state_dict(),
            "target_net": self.target_net.state_dict(),
            "optimizer": self.optimizer.state_dict(),
            "epsilon": self.epsilon,
            "steps_done": self.steps_done,
            "episodes_done": self.episodes_done,
            "episode_rewards": self.episode_rewards[-1000:],  # Últimas 1000
        }
        torch.save(checkpoint, path)
        print(f"[RL] Modelo salvo em: {path}")
    
    def load_model(self, path=None):
        """Carrega um modelo treinado"""
        path = path or self.model_path
        if not os.path.exists(path):
            print(f"[RL] Modelo não encontrado: {path}")
            return False
        
        checkpoint = torch.load(path, map_location=self.device, weights_only=False)
        self.policy_net.load_state_dict(checkpoint["policy_net"])
        self.target_net.load_state_dict(checkpoint["target_net"])
        
        if self.training and "optimizer" in checkpoint:
            self.optimizer.load_state_dict(checkpoint["optimizer"])
        
        self.epsilon = checkpoint.get("epsilon", self.epsilon_end)
        self.steps_done = checkpoint.get("steps_done", 0)
        self.episodes_done = checkpoint.get("episodes_done", 0)
        self.episode_rewards = checkpoint.get("episode_rewards", [])
        
        print(f"[RL] Modelo carregado: {path} (episódios: {self.episodes_done}, epsilon: {self.epsilon:.4f})")
        return True
