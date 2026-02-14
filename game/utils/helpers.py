"""
Funções auxiliares do jogo
"""

import random
import math


def distribute_initial_control():
    """
    Distribui o controle inicial dos continentes entre os jogadores.
    Garante que o controle total seja balanceado (~33% para cada jogador).
    Retorna um dicionário com as porcentagens de cada jogador em cada continente.
    """
    from game.utils.constants import CONTINENTS, PLAYERS
    
    continent_control = {}
    num_continents = len(CONTINENTS)
    num_players = len(PLAYERS)
    target_total = (100 * num_continents) / num_players  # Total ideal por jogador
    
    # Gera porcentagens aleatórias para cada continente
    for continent in CONTINENTS:
        percentages = []
        for _ in range(num_players):
            # Varia entre 20% e 46% para cada jogador
            percentages.append(random.randint(20, 46))
        
        # Normaliza para somar 100%
        total = sum(percentages)
        percentages = [int((p / total) * 100) for p in percentages]
        
        # Ajusta para garantir que soma seja exatamente 100%
        diff = 100 - sum(percentages)
        percentages[0] += diff
        
        continent_control[continent] = {
            PLAYERS[i]: percentages[i] for i in range(num_players)
        }
    
    # Calcula controle total atual de cada jogador
    player_totals = {player: sum(continent_control[c][player] for c in CONTINENTS) 
                     for player in PLAYERS}
    
    # Fase de ajuste: redistribui para balancear
    max_iterations = 50
    for iteration in range(max_iterations):
        # Encontra jogador com mais controle e jogador com menos controle
        max_player = max(player_totals.items(), key=lambda x: x[1])
        min_player = min(player_totals.items(), key=lambda x: x[1])
        
        # Se a diferença for pequena o suficiente, para
        if max_player[1] - min_player[1] <= 1:
            break
        
        # Transfere controle: acha um continente onde max_player tem mais que min_player
        for continent in CONTINENTS:
            if continent_control[continent][max_player[0]] > continent_control[continent][min_player[0]] + 1:
                # Transfere 1% do max_player para min_player
                continent_control[continent][max_player[0]] -= 1
                continent_control[continent][min_player[0]] += 1
                
                # Atualiza totais
                player_totals[max_player[0]] -= 1
                player_totals[min_player[0]] += 1
                break
    
    return continent_control


def get_continent_controller(continent_control):
    """
    Retorna o jogador que controla o continente (maior porcentagem).
    """
    return max(continent_control.items(), key=lambda x: x[1])[0]


def calculate_total_control(all_continents, player):
    """
    Calcula a porcentagem total de controle de um jogador sobre todos os continentes.
    """
    total = 0
    for continent_control in all_continents.values():
        total += continent_control.get(player, 0)
    
    # Divide pelo número de continentes para obter a média
    return total / len(all_continents)


def calculate_dice_count(control_percentage, bonus=0):
    """
    Calcula a quantidade de dados baseado na porcentagem de controle.
    """
    from game.utils.constants import DICE_CONTROL_DIVISOR, MIN_DICE
    
    dice = int(control_percentage / DICE_CONTROL_DIVISOR) + MIN_DICE + bonus
    return max(MIN_DICE, dice)


def roll_dice(count):
    """
    Rola uma quantidade de dados de 6 faces.
    """
    return [random.randint(1, 6) for _ in range(count)]


def resolve_combat(attacker_dice, defender_dice):
    """
    Resolve um combate comparando os dados.
    Retorna o número de vitórias do atacante.
    """
    attacker_sorted = sorted(attacker_dice, reverse=True)
    defender_sorted = sorted(defender_dice, reverse=True)
    
    wins = 0
    pairs = min(len(attacker_sorted), len(defender_sorted))
    
    for i in range(pairs):
        if attacker_sorted[i] > defender_sorted[i]:
            wins += 1
    
    return wins


def apply_combat_result(continent_control, attacker, defender, wins):
    """
    Aplica o resultado de um combate, transferindo controle.
    """
    from game.utils.constants import CONTROL_PERCENTAGE_PER_WIN
    
    transfer = wins * CONTROL_PERCENTAGE_PER_WIN
    
    # Transfere controle do defensor para o atacante
    continent_control[attacker] += transfer
    continent_control[defender] -= transfer
    
    # Garante que nenhuma porcentagem seja negativa
    if continent_control[defender] < 0:
        continent_control[attacker] += continent_control[defender]
        continent_control[defender] = 0
    
    # Normaliza para somar 100%
    normalize_percentages(continent_control)


def apply_event(continent_control, player, event_percentage):
    """
    Aplica um evento aleatório ao controle de um jogador em um continente.
    O evento é aplicado como porcentagem do controle atual.
    Os outros jogadores perdem/ganham proporcionalmente ao seu controle.
    """
    from game.utils.constants import PLAYERS
    
    current_control = continent_control[player]
    
    # Calcula o ganho/perda como porcentagem do controle atual
    change = int(current_control * event_percentage / 100)
    
    # Garante que a mudança não faça o controle ficar negativo ou acima de 100
    if change < 0:
        change = max(change, -current_control)  # Não pode perder mais do que tem
    else:
        change = min(change, 100 - current_control)  # Não pode ultrapassar 100
    
    # Se não há mudança, retorna
    if change == 0:
        return
    
    # Aplica a mudança ao jogador afetado
    continent_control[player] += change
    
    # Calcula o total de controle dos outros jogadores
    other_players = [p for p in PLAYERS if p != player]
    others_total = sum(continent_control[p] for p in other_players)
    
    # Se os outros não têm controle, não há o que distribuir
    if others_total == 0:
        return
    
    # Distribui a perda/ganho proporcionalmente entre os outros jogadores
    # (Se o jogador ganhou, os outros perdem; se perdeu, os outros ganham)
    remaining_to_distribute = -change
    
    for i, other_player in enumerate(other_players):
        if i == len(other_players) - 1:
            # Último jogador recebe o que sobrou (para evitar erros de arredondamento)
            other_change = remaining_to_distribute
        else:
            # Calcula a proporção deste jogador
            proportion = continent_control[other_player] / others_total
            other_change = int(-change * proportion)
            remaining_to_distribute -= other_change
        
        continent_control[other_player] += other_change
    
    # Garante que ninguém fique com valores negativos
    for p in PLAYERS:
        continent_control[p] = max(0, continent_control[p])
    
    # Normaliza para garantir que soma 100%
    normalize_percentages(continent_control)


def normalize_percentages(continent_control):
    """
    Normaliza as porcentagens para que somem exatamente 100%.
    """
    total = sum(continent_control.values())
    
    if total == 0:
        # Se todos estão em 0, distribui igualmente
        from game.utils.constants import PLAYERS
        for player in PLAYERS:
            continent_control[player] = 100 // len(PLAYERS)
        
        # Ajusta o resto
        diff = 100 - sum(continent_control.values())
        continent_control[PLAYERS[0]] += diff
    elif total != 100:
        # Normaliza proporcionalmente
        factor = 100 / total
        for player in list(continent_control.keys()):
            continent_control[player] = int(continent_control[player] * factor)
        
        # Ajusta diferença de arredondamento
        diff = 100 - sum(continent_control.values())
        # Adiciona a diferença ao jogador com maior controle
        max_player = max(continent_control.items(), key=lambda x: x[1])[0]
        continent_control[max_player] += diff


def lerp(start, end, t):
    """Interpolação linear"""
    return start + (end - start) * t


def clamp(value, min_value, max_value):
    """Limita um valor entre min e max"""
    return max(min_value, min(max_value, value))


def distance(point1, point2):
    """Calcula distância entre dois pontos"""
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)


def point_in_rect(point, rect):
    """Verifica se um ponto está dentro de um retângulo"""
    return (rect[0] <= point[0] <= rect[0] + rect[2] and
            rect[1] <= point[1] <= rect[1] + rect[3])
