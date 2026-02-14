"""
Sistema de combate do jogo
"""

from game.utils.helpers import calculate_dice_count, roll_dice, resolve_combat, apply_combat_result


class CombatSystem:
    """Gerencia o sistema de combate entre continentes"""
    
    def __init__(self):
        """Inicializa o sistema de combate"""
        self.last_combat_result = None
    
    def execute_attack(self, attacker_player, defender_player, 
                       attacking_continent, defending_continent):
        """
        Executa um ataque de um continente para outro.
        
        Args:
            attacker_player: Objeto Player do atacante
            defender_player: Objeto Player do defensor
            attacking_continent: Objeto Continent atacante
            defending_continent: Objeto Continent defensor
            
        Returns:
            Dicionário com resultado do combate
        """
        # Calcula quantidade de dados para cada lado
        attacker_control = attacking_continent.get_control_percentage(attacker_player.name)
        defender_control = defending_continent.get_control_percentage(defender_player.name)
        
        # Calcula dados com bônus especiais
        attacker_dice_count = calculate_dice_count(
            attacker_control, 
            bonus=attacker_player.get_attack_bonus()
        )
        defender_dice_count = calculate_dice_count(defender_control)
        
        # Rola os dados
        attacker_dice = roll_dice(attacker_dice_count)
        defender_dice = roll_dice(defender_dice_count)
        
        # Aplica bônus de defesa do MacOS
        if defender_player.name == "MacOS":
            defender_dice = [d + defender_player.get_defense_bonus() for d in defender_dice]
        
        # Resolve o combate
        attacker_wins = resolve_combat(attacker_dice, defender_dice)
        
        # Aplica o resultado ao continente defensor
        apply_combat_result(
            defending_continent.control,
            attacker_player.name,
            defender_player.name,
            attacker_wins
        )
        
        # Salva resultado para exibição
        self.last_combat_result = {
            "attacker": attacker_player.name,
            "defender": defender_player.name,
            "attacking_continent": attacking_continent.name,
            "defending_continent": defending_continent.name,
            "attacker_dice": attacker_dice,
            "defender_dice": defender_dice,
            "attacker_wins": attacker_wins,
            "control_gained": attacker_wins * 5,  # 5% por vitória
            "new_attacker_control": defending_continent.get_control_percentage(attacker_player.name),
            "new_defender_control": defending_continent.get_control_percentage(defender_player.name)
        }
        
        return self.last_combat_result
    
    def can_reroll_dice(self, player):
        """Verifica se o jogador pode re-rolar dados (habilidade do Linux)"""
        return player.can_reroll()
    
    def reroll_dice(self, player, dice_index, dice_list):
        """
        Re-rola um dado específico (habilidade do Linux).
        
        Args:
            player: Objeto Player
            dice_index: Índice do dado a ser re-rolado
            dice_list: Lista de dados
            
        Returns:
            Nova lista de dados
        """
        if not player.can_reroll():
            return dice_list
        
        new_dice = dice_list.copy()
        new_dice[dice_index] = roll_dice(1)[0]
        player.use_reroll()
        
        return new_dice
    
    def get_max_attacks_for_player(self, player_name, continents):
        """
        Calcula o número máximo de ataques permitidos para um jogador.
        Mínimo de 1, máximo igual ao número de continentes controlados.
        
        Args:
            player_name: Nome do jogador
            continents: Lista de objetos Continent
            
        Returns:
            Número de ataques permitidos
        """
        controlled_continents = sum(
            1 for continent in continents 
            if continent.get_controller() == player_name
        )
        
        return max(1, controlled_continents)
    
    def clear_last_result(self):
        """Limpa o último resultado de combate"""
        self.last_combat_result = None
