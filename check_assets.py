"""
Script para verificar se todos os assets necessários estão presentes
"""

import os
from game.utils.constants import CONTINENTS_DIR, LOGOS_DIR, CONTINENT_FILES, LOGO_FILES

def check_assets():
    """Verifica se todos os assets necessários estão presentes"""
    print("Verificando assets do jogo...\n")
    
    all_present = True
    
    # Verifica continentes
    print("Continentes:")
    for continent, filename in CONTINENT_FILES.items():
        path = os.path.join(CONTINENTS_DIR, filename)
        exists = os.path.exists(path)
        status = "✓" if exists else "✗"
        print(f"  {status} {continent}: {filename}")
        if not exists:
            all_present = False
    
    print("\nLogos:")
    # Verifica logos
    for player, filename in LOGO_FILES.items():
        path = os.path.join(LOGOS_DIR, filename)
        exists = os.path.exists(path)
        status = "✓" if exists else "✗"
        print(f"  {status} {player}: {filename}")
        if not exists:
            all_present = False
    
    print("\n" + "="*50)
    if all_present:
        print("✓ Todos os assets estão presentes!")
        print("Execute 'python main.py' para jogar.")
    else:
        print("✗ Alguns assets estão faltando.")
        print("Por favor, adicione os arquivos faltantes nas pastas:")
        print(f"  - Continentes: {CONTINENTS_DIR}")
        print(f"  - Logos: {LOGOS_DIR}")
    print("="*50)
    
    return all_present

if __name__ == "__main__":
    check_assets()
