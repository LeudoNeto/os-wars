# Jogo sobre o tema "Guerra de Sistemas Operacionais"

Descrição: Jogo baseado em War, com a guerra acontecendo entre os 3 sistemas operacionais: Windows, MacOS e Linux. Cada um controlado por um jogador.

## Como Executar

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar o jogo
python main.py
```

Para mais detalhes, consulte [INSTRUCOES.md](INSTRUCOES.md).
Ao invés de dominar totalmente cada país, a divisão será entre continentes:
- América do Norte
- América do Sul/Central
- Europa
- Ásia
- África
- Oceania

Habilidade Especial de cada SO:
- Windows: Ganha um dado extra para ataques independente da porcentagem de controle.
- MacOS: Soma mais 1 em todos os dados de defesa.
- Linux: Pode re-rolar um dado de ataque ou defesa uma vez por turno.

## Pasta assets
- `assets/continentes`: Imagens png dos continentes, recortados de um mapa mundi real.
- `assets/logos`: Imagens png das logos dos sistemas operacionais

## Mapa
O fundo será azul, representando o oceano, e em cima dele as imagens png dos continentes. Eles estão dispostos a representar o mapa mundi, tendo sido recortados de uma mesma imagem de um mapa mundi real. Assim não se preocupe com a posição, apenas coloque todos os continentes na "mesma posição", que é o centro da tela, e o mapa sairá formado.

Preencha cada continente com a cor do jogador que o controla (Windows: Vermelho, MacOS: Cinza, Linux: Verde), e a porcentagem de cada SO da seguinte forma: Destacado em cima a logo e a porcentagem do SO que controla o continente, e embaixo as porcentagens dos outros dois SOs. Exemplo: Se o continente é controlado pelo Windows, a logo do Windows e a porcentagem de controle do Windows ficam em destaque, e abaixo ficam as porcentagens de controle do MacOS e do Linux.

Cada SO terá uma porcentagem em um continente, que será inicialmente distribuída de forma aleatória, mas com uma média de 33% para cada um. O objetivo do jogo é conquistar 90% do total dos continentes. O jogo termina quando um dos jogadores atingir essa porcentagem.

## Interface
A interface do jogo é composta por:
- Um mapa centralizado na parte superior, com os continentes dispostos de forma a representar o mapa mundi.
- Na parte esquerda inferior, a logo do jogador ativo, junto com a porcentagem total de controle que ele tem sobre os continentes.
- Na parte central inferior, os 2 turnos "Ataque" e "Evento Aleatório", que ficam destacados quando é a vez do jogador realizar aquela etapa.
- Na parte direita inferior, quando o mouse não estiver sobre um continente, fica o botão de "Passar Etapa" (muda para "Passar Turno" quando está na etapa de Evento Aleatório). Quando o mouse estiver sobre um continente, aparecerá um gráfico de Pizza mostrando a porcentagem de controle de cada SO naquele continente. O botão de "Passar Etapa" fica escondido quando o mouse está sobre um continente, e só aparece quando o mouse não está sobre nenhum continente.

## Regras do Jogo
- O jogo é jogado em turnos, e cada turno em 2 etapas: Ataque e Evento Aleatório.
- Na etapa de Ataque, a quantidade da ataques permitidos no turno para o jogador é o mínimo entre 1 e a quantidade de continentes que ele controla. Ou seja, se um jogador controla 3 continentes, ele pode realizar até 3 ataques em seu turno, mas se ele controla apenas 1 continente, ele só pode realizar 1 ataque.
- Para atacar, o jogador ativo pode escolher um continente "atacante", e um a ser "atacado", que pode ser um continente adjacente ao seu continente atacante, ou o próprio continente atacante, para tentar aumentar sua porcentagem de controle. O ataque é resolvido por meio de um sistema de rolagem de dados.
- A quantidade de dados rolados depende da porcentagem de controle do jogador no continente atacante. O jogador pode escolher rolar um número de dados menor ou igual a divisão inteira de sua (porcentagem de controle / 20) + 1. Exemplo: Se um jogador tem 45% de controle em um continente, ele pode escolher rolar até 3 dados (45/20 = 2.25, arredondado para baixo é 2, mais 1 é 3).
- Assim como no War, o jogador defensor rola um número de dados baseado em sua porcentagem de controle no continente atacado, seguindo a mesma regra de divisão inteira de (porcentagem de controle / 20) + 1.
- Para resolver o ataque, os dados do atacante e do defensor são comparados em ordem decrescente. Para cada par de dados comparados, se o dado do atacante for maior que o do defensor, o atacante ganha 5% de controle no continente atacado, e o defensor perde 5%. Caso contrário, a porcentagem de ambos permanece a mesma. O número de pares de dados comparados é igual ao número mínimo de dados rolados entre o atacante e o defensor.
- O jogador ativo pode escolher passar a etapa de Ataque a qualquer momento, mesmo que ainda tenha ataques disponíveis. Após passar a etapa de Ataque, o jogador ativa a etapa de Evento Aleatório.
- Na etapa de Evento Aleatório, é girada uma roleta com 6 eventos diferentes, na roleta conterá as label "-30%", "-20%", "-10%", "+10%", "+20%" e "+30%". Quando a roleta parar, vai aparecer o nome e a descrição do evento sorteado, e ele será aplicado em um continente aleatório independente da porcentagem do jogador. O evento sorteado pode ser positivo ou negativo, e irá aumentar ou diminuir a porcentagem de controle do jogador ativo naquele continente em 10%, 20% ou 30%. O valor é referente a porcentagem que ele tem naquele continente, ou seja, se ele tem 50% de controle em um continente e o evento sorteado é "+20%", ele irá ganhar 20% de 50%, ou seja, 10%, aumentando seu controle para 60%. Se o evento sorteado fosse "-20%", ele perderia 20% de 50%, ou seja, 10%, diminuindo seu controle para 40%. O evento é aplicado apenas no jogador ativo, e não afeta os outros jogadores, estes terão suas porcentagens recalculadas normalmente para manter a soma em 100%.
- Após o evento ser aplicado, o jogador ativo passa o turno para o próximo jogador, seguindo a ordem Windows -> MacOS -> Linux -> Windows, e assim por diante.
- O jogo termina quando um jogador atingir 90% ou mais de controle total sobre os continentes. O jogador com a maior porcentagem de controle é declarado o vencedor.