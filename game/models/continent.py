"""
Classe do continente
"""

import pygame
from game.utils.constants import CONTINENT_POSITIONS, ADJACENT_CONTINENTS
from game.utils.helpers import get_continent_controller


class Continent:
    """Representa um continente no mapa"""
    
    def __init__(self, name, image_path):
        """
        Inicializa um continente.
        
        Args:
            name: Nome do continente
            image_path: Caminho para a imagem do continente
        """
        self.name = name
        self.image = None
        self.mask = None
        self.rect = None
        
        # Carrega imagem
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.rect = self.image.get_rect()
            self.rect.center = CONTINENT_POSITIONS[name]
            self.mask = pygame.mask.from_surface(self.image)
        except Exception as e:
            print(f"Erro ao carregar imagem do continente {name}: {e}")
            # Cria uma imagem placeholder
            self.image = pygame.Surface((200, 150), pygame.SRCALPHA)
            self.image.fill((100, 100, 100, 128))
            self.rect = self.image.get_rect()
            self.rect.center = CONTINENT_POSITIONS[name]
            self.mask = pygame.mask.from_surface(self.image)
        
        # Controle dos jogadores (será inicializado externamente)
        self.control = {}
        
    def get_controller(self):
        """Retorna o jogador que controla o continente"""
        return get_continent_controller(self.control)
    
    def get_control_percentage(self, player):
        """Retorna a porcentagem de controle de um jogador"""
        return self.control.get(player, 0)
    
    def is_adjacent_to(self, other_continent):
        """Verifica se este continente é adjacente a outro"""
        return other_continent.name in ADJACENT_CONTINENTS.get(self.name, [])
    
    def contains_point(self, pos):
        """
        Verifica se um ponto está dentro do continente.
        Usa mask collision para precisão pixel-perfect.
        """
        if not self.rect.collidepoint(pos):
            return False
        
        # Converte posição global para posição local no rect
        local_pos = (pos[0] - self.rect.x, pos[1] - self.rect.y)
        
        # Verifica se está dentro dos limites da imagem
        if (0 <= local_pos[0] < self.rect.width and 
            0 <= local_pos[1] < self.rect.height):
            try:
                return self.mask.get_at(local_pos)
            except IndexError:
                return False
        
        return False
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"Continent({self.name})"
