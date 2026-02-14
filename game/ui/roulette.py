"""
Roleta de eventos aleatórios
"""

import pygame
import math
import random
import time
from game.models.event import get_all_events
from game.utils.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WHITE, BLACK, GRAY,
    ROULETTE_CENTER, ROULETTE_RADIUS, ROULETTE_SPIN_TIME,
    ROULETTE_SLOWDOWN
)


class Roulette:
    """Roleta para eventos aleatórios"""
    
    def __init__(self, screen):
        """
        Inicializa a roleta.
        
        Args:
            screen: Surface do pygame
        """
        self.screen = screen
        self.events = get_all_events()  # Começa com eventos padrão
        self.current_angle = 0
        self.spinning = False
        self.spin_speed = 0
        self.selected_event = None
        self.start_time = 0
        
        # Fontes
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Cores para os eventos
        self.event_colors = [
            (231, 76, 60),    # Vermelho
            (241, 196, 15),   # Amarelo
            (46, 204, 113),   # Verde
            (52, 152, 219),   # Azul
            (155, 89, 182),   # Roxo
            (230, 126, 34)    # Laranja
        ]
    
    def set_player_events(self, player_name):
        """Define os eventos para um jogador específico
        
        Args:
            player_name: Nome do jogador
        """
        self.events = get_all_events(player_name)
    
    def start_spin(self):
        """Inicia a rotação da roleta"""
        self.spinning = True
        self.spin_speed = random.uniform(20, 30)  # Velocidade inicial aleatória
        self.start_time = time.time()
        self.selected_event = None
    
    def update(self):
        """Atualiza o estado da roleta"""
        if not self.spinning:
            return False
        
        # Atualiza ângulo
        self.current_angle += self.spin_speed
        self.current_angle %= 360
        
        # Reduz velocidade gradualmente
        self.spin_speed *= ROULETTE_SLOWDOWN
        
        # Para quando a velocidade é muito baixa
        if self.spin_speed < 0.1:
            self.spinning = False
            # Determina evento selecionado
            self._select_event()
            return True  # Retorna True quando termina
        
        return False
    
    def _select_event(self):
        """Seleciona o evento baseado no ângulo final"""
        # Calcula qual fatia está na posição do marcador (topo = 270 graus)
        # As fatias começam em current_angle - 90
        # Diferença angular do marcador ao início da primeira fatia
        angle_diff = (360 - self.current_angle) % 360
        
        # Determina qual evento baseado no ângulo
        section_angle = 360 / len(self.events)
        event_index = int(angle_diff / section_angle) % len(self.events)
        
        self.selected_event = self.events[event_index]
    
    def render(self, show_result=False, event_result=None):
        """
        Renderiza a roleta.
        
        Args:
            show_result: Se deve mostrar o resultado
            event_result: Dicionário com informações do resultado do evento
        """
        # Overlay escuro
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Desenha a roleta
        self._draw_wheel()
        
        # Desenha marcador (seta para baixo no topo)
        self._draw_marker()
        
        # Se não está girando e tem resultado, mostra
        if show_result and self.selected_event:
            self._draw_result(event_result)
        else:
            # Mostra instrução
            instruction = self.font_small.render(
                "Girando a roleta...", True, WHITE
            )
            instruction_rect = instruction.get_rect(
                center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 100)
            )
            self.screen.blit(instruction, instruction_rect)
    
    def _draw_wheel(self):
        """Desenha a roda da roleta"""
        center = ROULETTE_CENTER
        
        # Círculo de fundo
        pygame.draw.circle(self.screen, BLACK, center, ROULETTE_RADIUS + 5)
        pygame.draw.circle(self.screen, WHITE, center, ROULETTE_RADIUS + 5, 3)
        
        # Desenha cada fatia
        num_events = len(self.events)
        section_angle = 360 / num_events
        
        for i, event in enumerate(self.events):
            # Calcula ângulos da fatia
            start_angle = math.radians(self.current_angle + i * section_angle - 90)
            end_angle = math.radians(self.current_angle + (i + 1) * section_angle - 90)
            
            # Pontos da fatia
            points = [center]
            num_points = 20
            for j in range(num_points + 1):
                angle = start_angle + (end_angle - start_angle) * j / num_points
                x = center[0] + ROULETTE_RADIUS * math.cos(angle)
                y = center[1] + ROULETTE_RADIUS * math.sin(angle)
                points.append((x, y))
            
            # Desenha fatia
            color = self.event_colors[i % len(self.event_colors)]
            pygame.draw.polygon(self.screen, color, points)
            pygame.draw.polygon(self.screen, WHITE, points, 2)
            
            # Desenha label do evento
            mid_angle = start_angle + (end_angle - start_angle) / 2
            label_distance = ROULETTE_RADIUS * 0.7
            label_x = center[0] + label_distance * math.cos(mid_angle)
            label_y = center[1] + label_distance * math.sin(mid_angle)
            
            text = self.font_medium.render(event.label, True, WHITE)
            text_rect = text.get_rect(center=(label_x, label_y))
            
            # Fundo preto para legibilidade
            bg_rect = text_rect.inflate(10, 5)
            pygame.draw.rect(self.screen, BLACK, bg_rect)
            
            self.screen.blit(text, text_rect)
        
        # Círculo central
        pygame.draw.circle(self.screen, BLACK, center, 30)
        pygame.draw.circle(self.screen, WHITE, center, 30, 3)
    
    def _draw_marker(self):
        """Desenha o marcador que aponta para o evento selecionado"""
        center_x, center_y = ROULETTE_CENTER
        
        # Triângulo apontando para baixo no topo da roleta
        marker_y = center_y - ROULETTE_RADIUS - 20
        points = [
            (center_x, marker_y + 30),  # Ponta
            (center_x - 15, marker_y),  # Esquerda
            (center_x + 15, marker_y)   # Direita
        ]
        
        pygame.draw.polygon(self.screen, WHITE, points)
        pygame.draw.polygon(self.screen, BLACK, points, 2)
    
    def _draw_result(self, event_result=None):
        """Desenha o resultado do evento"""
        if not self.selected_event:
            return
        
        # Painel de resultado (maior para acomodar mais informações)
        panel_width = 700
        panel_height = 300
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = WINDOW_HEIGHT - 330
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, BLACK, panel_rect)
        pygame.draw.rect(self.screen, WHITE, panel_rect, 3)
        
        y_offset = panel_y + 30
        
        # Nome do evento
        name_text = self.font_large.render(
            self.selected_event.name, True, WHITE
        )
        name_rect = name_text.get_rect(
            center=(panel_x + panel_width//2, y_offset)
        )
        self.screen.blit(name_text, name_rect)
        y_offset += 40
        
        # Descrição
        desc_text = self.font_small.render(
            self.selected_event.description, True, GRAY
        )
        desc_rect = desc_text.get_rect(
            center=(panel_x + panel_width//2, y_offset)
        )
        self.screen.blit(desc_text, desc_rect)
        y_offset += 35
        
        # Informações do continente afetado
        if event_result:
            continent = event_result['continent']
            player = event_result['player']
            control_before = event_result['control_before']
            control_after = event_result['control_after']
            
            # Nome do continente
            continent_text = self.font_medium.render(
                f"Continente: {continent.name}", True, WHITE
            )
            continent_rect = continent_text.get_rect(
                center=(panel_x + panel_width//2, y_offset)
            )
            self.screen.blit(continent_text, continent_rect)
            y_offset += 35
            
            # Linha divisora
            pygame.draw.line(
                self.screen, GRAY,
                (panel_x + 50, y_offset),
                (panel_x + panel_width - 50, y_offset),
                1
            )
            y_offset += 20
            
            # Controle antes e depois
            from game.utils.constants import PLAYERS, PLAYER_COLORS
            
            # Cabeçalhos
            header_y = y_offset
            before_text = self.font_small.render("Antes", True, GRAY)
            before_rect = before_text.get_rect(center=(panel_x + panel_width//2 - 80, header_y))
            self.screen.blit(before_text, before_rect)
            
            after_text = self.font_small.render("Depois", True, GRAY)
            after_rect = after_text.get_rect(center=(panel_x + panel_width//2 + 80, header_y))
            self.screen.blit(after_text, after_rect)
            y_offset += 25
            
            # Porcentagens para cada jogador
            for player_name in PLAYERS:
                color = PLAYER_COLORS[player_name]
                
                # Nome do jogador
                player_text = self.font_small.render(f"{player_name}:", True, color)
                player_rect = player_text.get_rect(midleft=(panel_x + 80, y_offset))
                self.screen.blit(player_text, player_rect)
                
                # Antes
                before_pct = self.font_small.render(
                    f"{control_before[player_name]}%", True, WHITE
                )
                before_pct_rect = before_pct.get_rect(
                    center=(panel_x + panel_width//2 - 80, y_offset)
                )
                self.screen.blit(before_pct, before_pct_rect)
                
                # Depois
                after_pct = self.font_small.render(
                    f"{control_after[player_name]}%", True, WHITE
                )
                after_pct_rect = after_pct.get_rect(
                    center=(panel_x + panel_width//2 + 80, y_offset)
                )
                self.screen.blit(after_pct, after_pct_rect)
                
                # Seta indicando mudança
                change = control_after[player_name] - control_before[player_name]
                if change != 0:
                    arrow = "↑" if change > 0 else "↓"
                    change_color = (0, 255, 0) if change > 0 else (255, 0, 0)
                    change_text = self.font_small.render(
                        f"{arrow} {abs(change)}%", True, change_color
                    )
                    change_rect = change_text.get_rect(
                        midleft=(panel_x + panel_width//2 + 140, y_offset)
                    )
                    self.screen.blit(change_text, change_rect)
                
                y_offset += 22
        
        # Instrução
        instruction = self.font_small.render(
            "Clique para continuar", True, WHITE
        )
        instruction_rect = instruction.get_rect(
            center=(panel_x + panel_width//2, panel_y + panel_height - 20)
        )
        self.screen.blit(instruction, instruction_rect)
    
    def is_spinning(self):
        """Retorna se a roleta está girando"""
        return self.spinning
    
    def get_selected_event(self):
        """Retorna o evento selecionado"""
        return self.selected_event
    
    def reset(self):
        """Reseta a roleta"""
        self.spinning = False
        self.spin_speed = 0
        self.selected_event = None
