"""
OS Wars - Jogo de estratégia baseado em War
Ponto de entrada principal do jogo
"""

import sys
from game.game_manager import GameManager


def main():
    """Função principal"""
    try:
        game = GameManager()
        game.run()
    except Exception as e:
        print(f"Erro ao executar o jogo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
