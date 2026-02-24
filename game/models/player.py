"""
Classe do jogador
"""

from game.utils.constants import PLAYER_COLORS, SPECIAL_ABILITIES


class Player:
    """Representa um jogador (Sistema Operacional)"""
    
    def __init__(self, name, is_ai=False):
        """
        Inicializa um jogador.
        
        Args:
            name: Nome do SO (Windows, MacOS ou Linux)
            is_ai: Se o jogador é controlado por IA
        """
        self.name = name
        self.color = PLAYER_COLORS[name]
        self.ability = SPECIAL_ABILITIES[name]
        self.ability_used = False  # Para Linux que pode re-rolar 1x por combate
        self.is_ai = is_ai
    
    def reset_turn_abilities(self):
        """Reseta habilidades que são por turno"""
        self.ability_used = False
    
    def get_attack_bonus(self):
        """Retorna o bônus de dados de ataque se aplicável"""
        if self.name == "Windows":
            return 1  # Dado extra
        return 0
    
    def get_defense_bonus(self):
        """Retorna o bônus de defesa se aplicável"""
        if self.name == "MacOS":
            return 1  # +1 em cada dado
        return 0
    
    def can_reroll(self):
        """Verifica se o jogador pode re-rolar (Linux)"""
        return self.name == "Linux" and not self.ability_used
    
    def use_reroll(self):
        """Marca que a habilidade de re-roll foi usada"""
        if self.name == "Linux":
            self.ability_used = True
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"Player({self.name})"
