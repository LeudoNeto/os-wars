"""
Gerenciador de turnos do jogo
"""

from game.utils.constants import TURN_ORDER, PHASE_ATTACK, PHASE_EVENT


class TurnManager:
    """Gerencia os turnos e fases do jogo"""
    
    def __init__(self, players):
        """
        Inicializa o gerenciador de turnos.
        
        Args:
            players: Lista de objetos Player
        """
        self.players = {player.name: player for player in players}
        self.turn_order = TURN_ORDER
        self.current_player_index = 0
        self.current_phase = PHASE_ATTACK
        self.attacks_remaining = 0
        self.attacks_made = 0
        
    def get_current_player(self):
        """Retorna o jogador atual"""
        player_name = self.turn_order[self.current_player_index]
        return self.players[player_name]
    
    def get_current_phase(self):
        """Retorna a fase atual"""
        return self.current_phase
    
    def start_turn(self, max_attacks):
        """
        Inicia um novo turno para o jogador atual.
        
        Args:
            max_attacks: Número máximo de ataques permitidos
        """
        current_player = self.get_current_player()
        current_player.reset_turn_abilities()
        self.attacks_remaining = max_attacks
        self.attacks_made = 0
        self.current_phase = PHASE_ATTACK
    
    def use_attack(self):
        """Registra que um ataque foi realizado"""
        if self.attacks_remaining > 0:
            self.attacks_remaining -= 1
            self.attacks_made += 1
    
    def can_attack(self):
        """Verifica se ainda há ataques disponíveis"""
        return self.attacks_remaining > 0 and self.current_phase == PHASE_ATTACK
    
    def skip_attack_phase(self):
        """Pula a fase de ataque para a fase de evento"""
        if self.current_phase == PHASE_ATTACK:
            self.current_phase = PHASE_EVENT
            return True
        return False
    
    def next_turn(self):
        """Avança para o próximo turno"""
        self.current_player_index = (self.current_player_index + 1) % len(self.turn_order)
        self.current_phase = PHASE_ATTACK
        return self.get_current_player()
    
    def is_attack_phase(self):
        """Verifica se está na fase de ataque"""
        return self.current_phase == PHASE_ATTACK
    
    def is_event_phase(self):
        """Verifica se está na fase de evento"""
        return self.current_phase == PHASE_EVENT
    
    def get_attacks_info(self):
        """Retorna informações sobre os ataques"""
        return {
            "remaining": self.attacks_remaining,
            "made": self.attacks_made,
            "total": self.attacks_remaining + self.attacks_made
        }
