# Como Executar o Jogo

## Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes do Python)

## Instalação

1. Clone ou baixe o repositório do jogo

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Executar o Jogo

```bash
python main.py
```

## Como Jogar

### Objetivo
Conquistar 90% ou mais de controle total sobre todos os continentes.

### Turnos
O jogo é jogado em turnos que se alternam entre Windows, MacOS e Linux. Cada turno possui duas etapas:

1. **Etapa de Ataque**
   - Clique em um continente que você controla para selecioná-lo como atacante
   - Clique em um continente adjacente (ou no mesmo continente) para atacar
   - Você pode realizar de 1 até X ataques por turno (onde X é o número de continentes que você controla)
   - Clique em "Passar Etapa" para pular para a próxima etapa

2. **Etapa de Evento Aleatório**
   - Clique em "Girar Roleta" para sortear um evento
   - O evento será aplicado em um continente aleatório
   - Eventos podem ser positivos ou negativos, alterando seu controle naquele continente

### Sistema de Combate
- A quantidade de dados é baseada na porcentagem de controle: (controle / 20) + 1
- Os dados são comparados em ordem decrescente
- Para cada vitória, o atacante ganha 5% de controle

### Habilidades Especiais
- **Windows**: Ganha um dado extra para ataques
- **MacOS**: Soma +1 em todos os dados de defesa
- **Linux**: Pode re-rolar um dado de ataque ou defesa uma vez por turno

### Controles
- **Mouse**: Interagir com continentes e botões
- **ESC**: Sair do jogo

### Interface
- **Mapa**: Mostra os continentes coloridos segundo o jogador que os controla
- **Painel Inferior Esquerdo**: Informações do jogador atual
- **Painel Inferior Centro**: Fases do turno
- **Painel Inferior Direito**: Botão de passar etapa ou gráfico de pizza (ao passar o mouse sobre um continente)

## Estrutura do Projeto

```
os-wars/
├── assets/
│   ├── continentes/     # Imagens dos continentes
│   └── logos/           # Logos dos sistemas operacionais
├── game/
│   ├── logic/           # Lógica do jogo (combate, turnos)
│   ├── models/          # Modelos de dados (jogador, continente, evento)
│   ├── ui/              # Interface do usuário
│   ├── utils/           # Utilitários e constantes
│   └── game_manager.py  # Gerenciador principal
├── main.py              # Ponto de entrada
├── requirements.txt     # Dependências
└── README.md            # Documentação
```

## Requisitos de Assets

O jogo espera encontrar os seguintes arquivos:

### Continentes (assets/continentes/):
- america_norte.png
- america_sul.png
- europa.png
- asia.png
- africa.png
- oceania.png

### Logos (assets/logos/):
- windows.png
- macos.png
- linux.png

## Solução de Problemas

### Erro ao carregar imagens
Se você receber erros sobre imagens não encontradas, verifique se:
1. Os arquivos de imagem estão nas pastas corretas
2. Os nomes dos arquivos correspondem aos esperados
3. Os arquivos têm o formato PNG

### Jogo muito lento
- Ajuste a constante `FPS` em `game/utils/constants.py`
- Reduza a resolução da janela alterando `WINDOW_WIDTH` e `WINDOW_HEIGHT`

## Desenvolvimento

Para modificar o jogo:
- **Constantes**: `game/utils/constants.py`
- **Regras de combate**: `game/logic/combat.py`
- **Interface**: `game/ui/`
- **Lógica de turnos**: `game/logic/turn_manager.py`
