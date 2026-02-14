# OS Wars - Guerra de Sistemas Operacionais

Um jogo de estratégia baseado em War onde Windows, MacOS e Linux batalham pelo controle dos continentes do mundo.

## 📋 Sobre o Jogo

OS Wars é um jogo de estratégia por turnos onde três jogadores (representando Windows, MacOS e Linux) competem pelo domínio global. Cada sistema operacional começa com controle parcial sobre os 6 continentes do mundo e deve usar ataques estratégicos e eventos aleatórios para conquistar território inimigo.

## 🎮 Como Jogar

### Objetivo
Seja o primeiro a conquistar a maioria (50% ou mais) de controle em **todos os 6 continentes** simultaneamente.

### Continentes
- América do Norte
- América do Sul/Central
- Europa
- Ásia
- África
- Oceania

### Turnos e Fases

Cada turno é dividido em duas fases:

#### 1️⃣ Fase de Ataque
- Você pode realizar de 1 a X ataques (onde X = número de continentes que você controla)
- **Como atacar:**
  1. Clique em um continente que você controla (atacante)
  2. Clique em um continente adjacente ou no mesmo continente (alvo)
  3. Escolha quantos dados deseja rolar (de 1 até o máximo permitido)
  4. Após a animação dos dados, clique em "Continuar"
  5. Veja o resultado com o gráfico de pizza animado
- Você pode passar a fase a qualquer momento clicando em "Passar Etapa"

#### 2️⃣ Fase de Evento Aleatório
- Clique em "Girar Roleta" para sortear um evento
- Eventos possíveis: -30%, -20%, -10%, +10%, +20%, +30%
- O evento será aplicado em um continente aleatório
- A porcentagem é calculada sobre seu controle atual naquele continente
  - Exemplo: se você tem 50% e tira +20%, ganha 10% (20% de 50)
- Após ver o resultado, clique em "Passar Turno"

### Sistema de Combate

**Quantidade de Dados:**
- Baseada no controle do continente: `(porcentagem ÷ 20) + 1`
- Exemplo: 45% de controle = 3 dados (45÷20 = 2, +1 = 3)
- Você pode escolher rolar menos dados que o máximo permitido

**Resolução:**
- Os dados de atacante e defensor são ordenados do maior para o menor
- Cada par é comparado: se o atacante vencer, ganha 5% de controle
- O defensor perde 5% quando o atacante ganha
- Número de comparações = mínimo entre dados do atacante e do defensor

### 🎯 Habilidades Especiais

Cada sistema operacional possui uma habilidade única:

| SO | Habilidade | Descrição |
|---|---|---|
| **Windows** | Dado Bônus de Ataque | Sempre rola +1 dado em ataques |
| **MacOS** | Defesa Fortificada | Soma +1 em todos os dados de defesa |
| **Linux** | Re-rolagem | Pode re-rolar 1 dado (ataque ou defesa) por combate |

### 🖱️ Controles

- **Mouse**: Navegar, selecionar continentes e clicar em botões
- **Botão Direito**: Cancelar seleção de ataque
- **ESC**: Sair do jogo

### 📊 Interface

A tela é dividida em:

**Mapa (Superior):**
- Continentes coloridos pela cor do jogador dominante
  - 🔴 Windows: Vermelho
  - ⚪ MacOS: Cinza
  - 🟢 Linux: Verde
- Cada continente mostra a logo e porcentagem do controlador em destaque
- Porcentagens dos outros jogadores aparecem abaixo

**Painel Inferior:**
- **Esquerda**: Logo e porcentagem total de controle do jogador ativo
- **Centro**: Indicadores das fases (Ataque / Evento Aleatório)
- **Direita**: 
  - Botão "Passar Etapa" / "Passar Turno"
  - Gráfico de pizza ao passar o mouse sobre um continente

## 🚀 Como Executar

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes do Python)

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/LeudoNeto/os-wars.git
cd os-wars
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

### Executar o Jogo

```bash
python main.py
```

## 📁 Estrutura do Projeto

```
os-wars/
├── assets/
│   ├── continentes/     # Imagens PNG dos continentes
│   └── logos/           # Logos dos sistemas operacionais
├── game/
│   ├── logic/           # Sistema de combate e turnos
│   ├── models/          # Classes de Jogador, Continente e Evento
│   ├── ui/              # Interface gráfica e renderização
│   ├── utils/           # Constantes e funções auxiliares
│   └── game_manager.py  # Gerenciador principal do jogo
├── main.py              # Ponto de entrada
├── requirements.txt     # Dependências (pygame)
└── README.md            # Este arquivo
```

## 🎲 Regras Detalhadas

### Controle de Continentes
- Cada continente tem 100% de controle dividido entre os 3 jogadores
- Um jogador "controla" um continente quando tem a maior porcentagem
- A distribuição inicial é aleatória, com média de ~33% para cada jogador

### Ataques
- Só pode atacar de continentes adjacentes ou atacar o próprio continente
- O máximo de ataques por turno = continentes controlados (mínimo de 1)
- Cada ataque pode transferir até 5% × número de vitórias nos dados

### Eventos Aleatórios
- São aplicados apenas ao jogador ativo
- Afetam um continente aleatório, independente de quem o controla
- Após o evento, as porcentagens dos outros jogadores são rebalanceadas proporcionalmente

### Condição de Vitória
O jogo termina quando um jogador consegue:
- Ter **50% ou mais** de controle em **TODOS os 6 continentes** ao mesmo tempo

## 🛠️ Tecnologias

- **Python 3.8+**
- **Pygame 2.5.0+** - Engine de jogos e renderização

## 📝 Licença

Este projeto é de código aberto para fins educacionais.

**Divirta-se jogando OS Wars! 🎮🌍**