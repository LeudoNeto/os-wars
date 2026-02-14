"""
Classe de eventos aleatórios
"""

import random
from game.utils.constants import RANDOM_EVENTS


class RandomEvent:
    """Representa um evento aleatório do jogo"""
    
    def __init__(self, label, percentage, name, description):
        """
        Inicializa um evento.
        
        Args:
            label: Label curto do evento (ex: "+20%")
            percentage: Valor percentual do evento
            name: Nome do evento
            description: Descrição do evento
        """
        self.label = label
        self.percentage = percentage
        self.name = name
        self.description = description
    
    def is_positive(self):
        """Retorna se o evento é positivo"""
        return self.percentage > 0
    
    def __str__(self):
        return f"{self.name}: {self.description}"
    
    def __repr__(self):
        return f"RandomEvent({self.name}, {self.percentage}%)"


def get_random_event(player=None):
    """Retorna um evento aleatório
    
    Args:
        player: Nome do jogador (opcional, usa o primeiro se não especificado)
    """
    if player and player in RANDOM_EVENTS:
        event_data = random.choice(RANDOM_EVENTS[player])
    else:
        # Fallback: pega do primeiro jogador
        first_player = list(RANDOM_EVENTS.keys())[0]
        event_data = random.choice(RANDOM_EVENTS[first_player])
    return RandomEvent(**event_data)


def get_all_events(player=None):
    """Retorna todos os eventos possíveis para um jogador
    
    Args:
        player: Nome do jogador (opcional, usa o primeiro se não especificado)
    """
    if player and player in RANDOM_EVENTS:
        events_data = RANDOM_EVENTS[player]
    else:
        # Fallback: pega do primeiro jogador
        first_player = list(RANDOM_EVENTS.keys())[0]
        events_data = RANDOM_EVENTS[first_player]
    return [RandomEvent(**event_data) for event_data in events_data]
