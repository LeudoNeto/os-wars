"""
Classe de eventos aleatórios
"""

import random
from game.utils.constants import RANDOM_EVENTS


class RandomEvent:
    """Representa um evento aleatório do jogo"""
    
    def __init__(self, label, percentage, name, description, date=None):
        """
        Inicializa um evento.
        
        Args:
            label: Label curto do evento (ex: "+20%")
            percentage: Valor percentual do evento
            name: Nome do evento
            description: Descrição do evento
            date: Data do evento no formato YYYY-MM-DD
        """
        self.label = label
        self.percentage = percentage
        self.name = name
        self.description = description
        self.date = date if date else "9999-12-31"
    
    @property
    def formatted_date(self):
        """Retorna a data formatada em português (ex: '29 de julho de 2015')."""
        if not self.date or self.date == "9999-12-31":
            return ""
        
        months = {
            '01': 'janeiro', '02': 'fevereiro', '03': 'março', '04': 'abril',
            '05': 'maio', '06': 'junho', '07': 'julho', '08': 'agosto',
            '09': 'setembro', '10': 'outubro', '11': 'novembro', '12': 'dezembro'
        }
        
        try:
            parts = self.date.split('-')
            if len(parts) == 3:
                year, month, day = parts
                month_name = months.get(month, month)
                return f"{int(day)} de {month_name} de {year}"
        except:
            pass
        
        return self.date
    
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


def get_events_sorted_by_date(player):
    """Retorna todos os eventos de um jogador ordenados por data (mais antigo primeiro).
    
    Args:
        player: Nome do jogador
    
    Returns:
        Lista de RandomEvent ordenados cronologicamente
    """
    events = get_all_events(player)
    return sorted(events, key=lambda e: e.date)
