"""
Constantes do jogo OS Wars
"""

import os

# Diretórios
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
CONTINENTS_DIR = os.path.join(ASSETS_DIR, "continentes")
LOGOS_DIR = os.path.join(ASSETS_DIR, "logos")

# Configurações da janela
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
FPS = 60
WINDOW_TITLE = "OS Wars - Guerra dos Sistemas Operacionais"

# Cores
OCEAN_BLUE = (41, 128, 185)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)

# Cores dos jogadores
PLAYER_COLORS = {
    "Windows": (231, 76, 60),    # Vermelho
    "MacOS": (149, 165, 166),     # Cinza
    "Linux": (46, 204, 113)       # Verde
}

# Cores mais escuras para overlay
PLAYER_OVERLAY_COLORS = {
    "Windows": (192, 57, 43),
    "MacOS": (127, 140, 141),
    "Linux": (39, 174, 96)
}

# Nomes dos continentes
CONTINENTS = [
    "America do Norte",
    "America do Sul",
    "Europa",
    "Asia",
    "Africa",
    "Oceania"
]

# Mapeamento de nomes de arquivos dos continentes
CONTINENT_FILES = {
    "America do Norte": "america_do_norte.png",
    "America do Sul": "america_do_sul.png",
    "Europa": "europa.png",
    "Asia": "asia.png",
    "Africa": "africa.png",
    "Oceania": "oceania.png"
}

# Posições dos continentes no mapa
CONTINENT_POSITIONS = {
    "America do Norte": (450, 225),
    "America do Sul": (492, 545),
    "Europa": (800, 250),
    "Asia": (1038, 303),
    "Africa": (785, 505),
    "Oceania": (1250, 600)
}

# Offset das informações de controle para cada continente (x, y)
# Ajuste esses valores para centralizar as porcentagens em cada continente
CONTINENT_INFO_OFFSET = {
    "America do Norte": (-72, 72),
    "America do Sul": (20, -10),
    "Europa": (-20, 24),
    "Asia": (0, 0),
    "Africa": (0, -30),
    "Oceania": (-24, 0)
}

# Continentes adjacentes
ADJACENT_CONTINENTS = {
    "America do Norte": ["America do Sul", "Asia", "Europa"],
    "America do Sul": ["America do Norte", "Africa"],
    "Europa": ["America do Norte", "Asia", "Africa"],
    "Asia": ["America do Norte", "Europa", "Africa", "Oceania"],
    "Africa": ["America do Sul", "Europa", "Asia"],
    "Oceania": ["Asia"]
}

# Jogadores
PLAYERS = ["Windows", "MacOS", "Linux"]

# Ordem dos turnos
TURN_ORDER = ["Windows", "MacOS", "Linux"]

# Habilidades especiais
SPECIAL_ABILITIES = {
    "Windows": "Ganha um dado extra para ataques",
    "MacOS": "Soma +1 em todos os dados de defesa",
    "Linux": "Pode re-rolar um dado por combate"
}

# Logo dos SOs
LOGO_FILES = {
    "Windows": "windows.png",
    "MacOS": "macos.png",
    "Linux": "linux.png"
}

# Configurações de gameplay
CONTROL_PERCENTAGE_PER_WIN = 5  # Porcentagem ganha/perdida por vitória no combate
DICE_CONTROL_DIVISOR = 20  # Divisor para calcular quantidade de dados
MIN_DICE = 1  # Mínimo de dados
WIN_PERCENTAGE = 90  # Porcentagem necessária para vencer

# Eventos aleatórios por SO
RANDOM_EVENTS = {
    "Windows": [
        # Eventos Negativos (baseados em incidentes reais)
        {"label": "-30%", "percentage": -30, "name": "Falha CrowdStrike Global", 
         "description": "Atualização defeituosa da CrowdStrike causa Blue Screen of Death em milhões de PCs mundialmente! -30% de controle"},
        {"label": "-20%", "percentage": -20, "name": "Update KB Quebrado", 
         "description": "Atualização do Windows quebra recursos essenciais do sistema! -20% de controle"},
        {"label": "-10%", "percentage": -10, "name": "Vulnerabilidade RDP", 
         "description": "Falha crítica no Remote Desktop permite invasões! -10% de controle"},
        
        # Eventos Positivos (baseados em sucessos reais)
        {"label": "+10%", "percentage": 10, "name": "DirectX 12 Lançado", 
         "description": "Nova versão do DirectX revoluciona performance em jogos! +10% de controle"},
        {"label": "+20%", "percentage": 20, "name": "Windows Subsystem for Linux", 
         "description": "WSL conquista desenvolvedores ao trazer Linux nativo para Windows! +20% de controle"},
        {"label": "+30%", "percentage": 30, "name": "Copilot+ PC Launch", 
         "description": "Windows com IA integrada atrai milhões de usuários empresariais! +30% de controle"}
    ],
    "MacOS": [
        # Eventos Negativos (baseados em incidentes reais)
        {"label": "-30%", "percentage": -30, "name": "Root Login Sem Senha", 
         "description": "Bug crítico no macOS High Sierra permite acesso root sem senha! -30% de controle"},
        {"label": "-20%", "percentage": -20, "name": "Gatekeeper Bypass", 
         "description": "Falha permite malware burlar proteções de segurança do macOS! -20% de controle"},
        {"label": "-10%", "percentage": -10, "name": "WebKit Zero-Day", 
         "description": "Vulnerabilidade WebKit sendo explorada ativamente contra Macs! -10% de controle"},
        
        # Eventos Positivos (baseados em sucessos reais)
        {"label": "+10%", "percentage": 10, "name": "Continuity Camera", 
         "description": "iPhone como webcam do Mac viraliza nas redes sociais! +10% de controle"},
        {"label": "+20%", "percentage": 20, "name": "Apple Silicon M1", 
         "description": "Chips M1 superam Intel em performance e eficiência energética! +20% de controle"},
        {"label": "+30%", "percentage": 30, "name": "Apple Intelligence", 
         "description": "IA integrada ao macOS conquista profissionais criativos! +30% de controle"}
    ],
    "Linux": [
        # Eventos Negativos (baseados em incidentes reais)
        {"label": "-30%", "percentage": -30, "name": "Dirty Pipe Kernel Bug", 
         "description": "Vulnerabilidade crítica permite escalonamento de privilégios no kernel! -30% de controle"},
        {"label": "-20%", "percentage": -20, "name": "Log4Shell Exploit", 
         "description": "Falha Apache Log4j afeta milhões de servidores Linux! -20% de controle"},
        {"label": "-10%", "percentage": -10, "name": "Sudo Privilege Bug", 
         "description": "Bug no sudo permite usuários locais obterem acesso root! -10% de controle"},
        
        # Eventos Positivos (baseados em sucessos reais)
        {"label": "+10%", "percentage": 10, "name": "Steam Deck Success", 
         "description": "Steam Deck com Linux prova viabilidade de gaming portátil! +10% de controle"},
        {"label": "+20%", "percentage": 20, "name": "Android Domination", 
         "description": "Linux kernel no Android atinge 70% dos dispositivos móveis! +20% de controle"},
        {"label": "+30%", "percentage": 30, "name": "Supercomputação Total", 
         "description": "Linux alcança 100% dos Top 500 supercomputadores do mundo! +30% de controle"}
    ]
}

# Etapas do turno
PHASE_ATTACK = "Ataque"
PHASE_EVENT = "Evento Aleatório"

# UI Layout
MAP_CENTER_Y = 300  # Centro vertical do mapa
BOTTOM_PANEL_Y = 650  # Posição Y do painel inferior
BOTTOM_PANEL_HEIGHT = 250

# Posições dos elementos da UI inferior
PLAYER_INFO_X = 80
PLAYER_INFO_Y = 720

PHASE_DISPLAY_X = WINDOW_WIDTH // 2
PHASE_DISPLAY_Y = 750

BUTTON_X = WINDOW_WIDTH - 200
BUTTON_Y = 816
BUTTON_WIDTH = 180
BUTTON_HEIGHT = 60

# Tamanhos
LOGO_SIZE = (80, 80)
SMALL_LOGO_SIZE = (40, 40)
PIE_CHART_RADIUS = 80

# Fontes (tamanhos)
FONT_TITLE = 48
FONT_LARGE = 36
FONT_MEDIUM = 28
FONT_SMALL = 20
FONT_TINY = 16

# Roulette
ROULETTE_CENTER = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
ROULETTE_RADIUS = 200
ROULETTE_SPIN_TIME = 3000  # ms
ROULETTE_SLOWDOWN = 0.95  # Fator de desaceleração
