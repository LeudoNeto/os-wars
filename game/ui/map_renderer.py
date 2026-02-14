"""
Renderizador do mapa
"""

import pygame
import math
from game.utils.constants import (
    PLAYER_COLORS, WHITE, BLACK, 
    SMALL_LOGO_SIZE, PIE_CHART_RADIUS, CONTINENT_INFO_OFFSET
)


class MapRenderer:
    """Renderiza o mapa e os continentes"""
    
    def __init__(self, screen, continents, logos):
        """
        Inicializa o renderizador do mapa.
        
        Args:
            screen: Surface do pygame onde desenhar
            continents: Lista de objetos Continent
            logos: Dicionário com as logos dos jogadores
        """
        self.screen = screen
        self.continents = continents
        self.logos = logos
        self.font_medium = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 20)
    
    def render(self, hovered_continent=None):
        """
        Renderiza todos os continentes.
        
        Args:
            hovered_continent: Continente sob o mouse (opcional)
        """
        for continent in self.continents:
            self._render_continent(continent, continent == hovered_continent)
    
    def _render_continent(self, continent, is_hovered):
        """Renderiza um continente individual"""
        # Cria surface colorida baseada no controlador
        controller = continent.get_controller()
        color = PLAYER_COLORS[controller]
        
        # Escurece um pouco as cores para um tom médio (75% da cor original)
        adjusted_color = tuple(int(c * 0.9) for c in color)
        
        # Cria uma superfície com a cor ajustada do jogador
        colored_surface = pygame.Surface(continent.image.get_size(), pygame.SRCALPHA)
        colored_surface.fill((0, 0, 0, 0))  # Começa transparente
        
        # Preenche com a cor do jogador
        colored_surface.fill((*adjusted_color, 255))
        
        # Copia o canal alpha da imagem original (para manter a forma do continente)
        # Isso faz com que apenas a área do continente fique visível
        original_alpha = pygame.surfarray.pixels_alpha(continent.image)
        new_alpha = pygame.surfarray.pixels_alpha(colored_surface)
        new_alpha[:] = original_alpha[:]
        del original_alpha
        del new_alpha
        
        # Desenha o continente colorido
        self.screen.blit(colored_surface, continent.rect)
        
        # Destaque se hover
        if is_hovered:
            # Desenha borda ao redor
            pygame.draw.rect(self.screen, WHITE, continent.rect, 3)
        
        # Desenha informações de controle
        self._render_continent_info(continent)
    
    def _render_continent_info(self, continent):
        """Renderiza informações de controle sobre o continente"""
        controller = continent.get_controller()
        control_percentage = continent.get_control_percentage(controller)
        
        # Posição central do continente com offset personalizado
        offset_x, offset_y = CONTINENT_INFO_OFFSET.get(continent.name, (0, 0))
        center_x = continent.rect.centerx + offset_x
        center_y = continent.rect.centery + offset_y
        
        # Desenha logo pequena do controlador
        if controller in self.logos:
            logo = pygame.transform.scale(self.logos[controller], SMALL_LOGO_SIZE)
            logo_rect = logo.get_rect(center=(center_x, center_y - 30))
            self.screen.blit(logo, logo_rect)
        
        # Desenha porcentagem principal
        percentage_text = self.font_medium.render(
            f"{control_percentage}%", True, WHITE
        )
        percentage_rect = percentage_text.get_rect(center=(center_x, center_y))
        
        # Fundo preto para legibilidade
        bg_rect = percentage_rect.inflate(10, 5)
        pygame.draw.rect(self.screen, BLACK, bg_rect)
        pygame.draw.rect(self.screen, WHITE, bg_rect, 1)
        
        self.screen.blit(percentage_text, percentage_rect)
        
        # Desenha porcentagens dos outros jogadores (pequenas, embaixo)
        y_offset = center_y + 25
        logo_size = 16  # Tamanho pequeno para as logos
        gap = 4  # Espaço entre logo e texto
        
        for player in continent.control.keys():
            if player != controller:
                percentage = continent.get_control_percentage(player)
                
                # Renderiza texto para calcular largura
                small_text = self.font_small.render(
                    f"{percentage}%", True, WHITE
                )
                text_width = small_text.get_width()
                
                # Calcula largura total do conjunto (logo + gap + texto)
                total_width = logo_size + gap + text_width
                
                # Calcula posição inicial para centralizar o conjunto
                start_x = center_x - total_width // 2
                
                # Logo pequena
                if player in self.logos:
                    small_logo = pygame.transform.scale(self.logos[player], (logo_size, logo_size))
                    logo_rect = small_logo.get_rect(midleft=(start_x, y_offset))
                
                # Porcentagem (após a logo)
                small_rect = small_text.get_rect(midleft=(start_x + logo_size + gap, y_offset))
                
                # Fundo
                small_bg = pygame.Rect(start_x - 4, y_offset - 10, total_width + 8, 20)
                pygame.draw.rect(self.screen, BLACK, small_bg)
                
                # Desenha logo e texto sobre o fundo
                if player in self.logos:
                    self.screen.blit(small_logo, logo_rect)
                self.screen.blit(small_text, small_rect)
                
                y_offset += 18
    
    def render_pie_chart(self, continent, position):
        """
        Renderiza um gráfico de pizza do controle do continente.
        
        Args:
            continent: Objeto Continent
            position: Tupla (x, y) com a posição central do gráfico
        """
        from game.utils.constants import PLAYER_COLORS, PLAYERS
        
        # Desenha círculo de fundo
        pygame.draw.circle(self.screen, WHITE, position, PIE_CHART_RADIUS + 2)
        pygame.draw.circle(self.screen, BLACK, position, PIE_CHART_RADIUS)
        
        # Calcula ângulos para cada jogador
        start_angle = 0
        for player in PLAYERS:
            percentage = continent.get_control_percentage(player)
            angle = (percentage / 100) * 2 * math.pi
            
            if percentage > 0:
                # Desenha fatia do pizza
                points = [position]
                
                # Gera pontos da fatia
                num_points = max(2, int(angle * 30))  # Mais pontos para arcos suaves
                for i in range(num_points + 1):
                    current_angle = start_angle + (angle * i / num_points)
                    x = position[0] + PIE_CHART_RADIUS * math.cos(current_angle - math.pi/2)
                    y = position[1] + PIE_CHART_RADIUS * math.sin(current_angle - math.pi/2)
                    points.append((x, y))
                
                # Desenha a fatia
                if len(points) > 2:
                    pygame.draw.polygon(self.screen, PLAYER_COLORS[player], points)
                    pygame.draw.polygon(self.screen, WHITE, points, 2)
                
                start_angle += angle
        
        # Desenha labels
        y_offset = position[1] + PIE_CHART_RADIUS + 20
        for player in PLAYERS:
            percentage = continent.get_control_percentage(player)
            color = PLAYER_COLORS[player]
            
            # Quadrado de cor
            pygame.draw.rect(self.screen, color, 
                           (position[0] - 80, y_offset - 8, 15, 15))
            pygame.draw.rect(self.screen, WHITE, 
                           (position[0] - 80, y_offset - 8, 15, 15), 1)
            
            # Texto
            label = self.font_small.render(
                f"{player}: {percentage}%", True, WHITE
            )
            self.screen.blit(label, (position[0] - 60, y_offset - 10))
            
            y_offset += 20
        
        # Nome do continente no topo
        title = self.font_medium.render(continent.name, True, WHITE)
        title_rect = title.get_rect(center=(position[0], position[1] - PIE_CHART_RADIUS - 20))
        
        # Fundo para o título
        bg_rect = title_rect.inflate(10, 5)
        pygame.draw.rect(self.screen, BLACK, bg_rect)
        pygame.draw.rect(self.screen, WHITE, bg_rect, 2)
        
        self.screen.blit(title, title_rect)
    
    def get_continent_at_position(self, pos):
        """
        Retorna o continente na posição do mouse.
        
        Args:
            pos: Tupla (x, y) com a posição do mouse
            
        Returns:
            Objeto Continent ou None
        """
        for continent in self.continents:
            if continent.contains_point(pos):
                return continent
        return None
