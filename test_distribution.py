"""
Script para testar a distribuição inicial de controle
"""

import sys
sys.path.insert(0, '.')

from game.utils.helpers import distribute_initial_control, calculate_total_control
from game.utils.constants import CONTINENTS, PLAYERS

def test_distribution():
    """Testa a distribuição inicial várias vezes"""
    print("Testando distribuição inicial de controle...\n")
    
    num_tests = 5
    
    for test in range(1, num_tests + 1):
        print(f"=== Teste {test} ===")
        
        # Gera distribuição
        continent_control = distribute_initial_control()
        
        # Calcula controle total de cada jogador
        for player in PLAYERS:
            total = calculate_total_control(continent_control, player)
            print(f"{player}: {total:.2f}%")
        
        print()
        
        # Mostra alguns continentes de exemplo
        print("Exemplos de continentes:")
        for i, continent in enumerate(CONTINENTS[:3]):
            print(f"  {continent}:")
            for player in PLAYERS:
                print(f"    {player}: {continent_control[continent][player]}%")
        
        print("\n" + "-"*50 + "\n")

if __name__ == "__main__":
    test_distribution()
