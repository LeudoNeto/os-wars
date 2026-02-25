"""
Script de treinamento do agente RL para OS Wars.

Executa episódios headless (sem interface gráfica) para treinar
o agente via DQN (Deep Q-Network).

Uso:
    python train_rl.py [--episodes 5000] [--player Linux] [--save-interval 500]
"""

import argparse
import os
import sys
import time
import json
import numpy as np

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Desabilita inicialização do pygame display (para treinamento headless)
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'


def train(args):
    """Executa o treinamento do agente RL"""
    
    # Import após configurar ambiente
    import torch
    from game.rl.rl_agent import RLAgent, NUM_ACTIONS
    from game.rl.environment import OSWarsEnv
    
    # Info do dispositivo
    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)
        device_str = f"CUDA ({device_name})"
    else:
        device_str = "CPU"
    
    episodes_str = "∞ (Ctrl+C para parar)" if args.episodes == 0 else str(args.episodes)
    
    print("=" * 60)
    print(f"  OS Wars - Treinamento RL (DQN)")
    print(f"  Dispositivo: {device_str}")
    print(f"  Jogador: {args.player}")
    print(f"  Episódios: {episodes_str}")
    print(f"  Max turnos por episódio: {args.max_turns}")
    print(f"  Batch size: {args.batch_size}")
    print(f"  Learning rate: {args.lr}")
    print(f"  Gamma (desconto): {args.gamma}")
    print(f"  Epsilon: {args.epsilon_start} → {args.epsilon_end}")
    print("=" * 60)
    
    # Cria diretório de modelos
    models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
    os.makedirs(models_dir, exist_ok=True)
    
    model_path = os.path.join(models_dir, f"rl_agent_{args.player.lower()}.pth")
    
    # Inicializa agente
    agent = RLAgent(
        player_name=args.player,
        training=True,
        model_path=model_path if args.resume else None,
        lr=args.lr,
        gamma=args.gamma,
        epsilon_start=args.epsilon_start,
        epsilon_end=args.epsilon_end,
        epsilon_decay=args.epsilon_decay,
        batch_size=args.batch_size,
        target_update=args.target_update
    )
    
    if args.resume and os.path.exists(model_path):
        print(f"\nRetomando treinamento de: {model_path}")
        print(f"  Episódios anteriores: {agent.episodes_done}")
        print(f"  Epsilon atual: {agent.epsilon:.4f}")
    
    # Inicializa ambiente
    env = OSWarsEnv(rl_player_name=args.player, max_turns=args.max_turns)
    
    # Métricas
    total_rewards = []
    wins = 0
    losses_log = []
    steps_total = 0
    
    start_time = time.time()
    infinite_mode = (args.episodes == 0)
    
    if infinite_mode:
        print(f"\nIniciando treinamento INDEFINIDO (Ctrl+C para parar e salvar)...")
    else:
        print(f"\nIniciando treinamento...")
    print("-" * 60)
    
    episode = 0
    try:
        while True:
            episode += 1
            
            # Verifica limite (se não for infinito)
            if not infinite_mode and episode > args.episodes:
                break
            
            state = env.reset()
            episode_reward = 0.0
            episode_steps = 0
            
            done = False
            while not done:
                # Obtém ações válidas
                valid_mask = env.get_valid_actions()
                
                # Seleciona ação
                action = agent.select_action(state, valid_mask)
                
                # Executa ação
                next_state, reward, done, info = env.step(action)
                
                # Armazena transição
                agent.store_transition(state, action, reward, next_state, float(done))
                
                # Treina
                loss = agent.train_step()
                if loss is not None:
                    losses_log.append(loss)
                
                state = next_state
                episode_reward += reward
                episode_steps += 1
                steps_total += 1
            
            # Registra fim do episódio
            agent.end_episode(episode_reward)
            total_rewards.append(episode_reward)
            
            if env.winner == args.player:
                wins += 1
            
            # Log periódico
            if episode % args.log_interval == 0:
                elapsed = time.time() - start_time
                avg_reward = np.mean(total_rewards[-args.log_interval:])
                avg_loss = np.mean(losses_log[-100:]) if losses_log else 0.0
                win_rate = wins / episode * 100
                recent_win_rate = sum(
                    1 for r in total_rewards[-args.log_interval:] if r > 30
                ) / min(args.log_interval, len(total_rewards)) * 100
                
                ep_display = f"Ep {episode:>7,}" if infinite_mode else f"Ep {episode:5d}/{args.episodes}"
                
                print(f"{ep_display} | "
                      f"Reward: {avg_reward:+7.2f} | "
                      f"Loss: {avg_loss:.4f} | "
                      f"Epsilon: {agent.epsilon:.4f} | "
                      f"WinRate: {win_rate:.1f}% (recente: {recent_win_rate:.1f}%) | "
                      f"Steps: {steps_total:,} | "
                      f"Tempo: {elapsed:.0f}s")
            
            # Salva modelo periodicamente
            if episode % args.save_interval == 0:
                agent.save_model(model_path)
                
                # Salva métricas
                _save_metrics(models_dir, args.player, episode, agent, 
                             steps_total, wins, total_rewards, start_time)
    
    except KeyboardInterrupt:
        print(f"\n\n⏹ Treinamento interrompido pelo usuário no episódio {episode}.")
        print("Salvando modelo...")
    
    # Salva modelo final
    agent.save_model(model_path)
    _save_metrics(models_dir, args.player, episode, agent,
                 steps_total, wins, total_rewards, start_time)
    
    # Relatório final
    elapsed = time.time() - start_time
    eps_per_sec = episode / elapsed if elapsed > 0 else 0
    print("\n" + "=" * 60)
    print("Treinamento concluído!")
    print(f"\n  Episódios: {episode:,}")
    print(f"  Steps totais: {steps_total:,}")
    print(f"  Vitórias: {wins}/{episode} ({wins/max(1,episode)*100:.1f}%)")
    print(f"  Reward médio (últimos 100): {np.mean(total_rewards[-100:]):+.2f}")
    print(f"  Epsilon final: {agent.epsilon:.4f}")
    print(f"  Tempo total: {elapsed:.0f}s ({eps_per_sec:.1f} episódios/s)")
    print(f"  Modelo salvo em: {model_path}")
    print("=" * 60)


def _save_metrics(models_dir, player, episode, agent, steps_total, wins, total_rewards, start_time):
    """Salva métricas de treinamento em JSON"""
    metrics = {
        "episodes": episode + agent.episodes_done,
        "total_steps": steps_total,
        "epsilon": agent.epsilon,
        "win_rate": wins / max(1, episode) * 100,
        "avg_reward_last_100": float(np.mean(total_rewards[-100:])) if total_rewards else 0.0,
        "total_wins": wins,
        "training_time_seconds": time.time() - start_time
    }
    metrics_path = os.path.join(models_dir, f"metrics_{player.lower()}.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)


def evaluate(args):
    """Avalia o agente treinado"""
    from game.rl.rl_agent import RLAgent
    from game.rl.environment import OSWarsEnv
    
    models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
    model_path = os.path.join(models_dir, f"rl_agent_{args.player.lower()}.pth")
    
    if not os.path.exists(model_path):
        print(f"Modelo não encontrado: {model_path}")
        print("Treine primeiro com: python train_rl.py")
        return
    
    agent = RLAgent(
        player_name=args.player,
        training=False,
        model_path=model_path
    )
    
    env = OSWarsEnv(rl_player_name=args.player, max_turns=args.max_turns)
    
    n_eval = args.eval_episodes
    wins = 0
    total_rewards = []
    total_turns = []
    
    print(f"\nAvaliando agente {args.player} em {n_eval} episódios...")
    
    for ep in range(n_eval):
        state = env.reset()
        episode_reward = 0.0
        done = False
        
        while not done:
            valid_mask = env.get_valid_actions()
            action = agent.select_action(state, valid_mask)
            state, reward, done, info = env.step(action)
            episode_reward += reward
        
        total_rewards.append(episode_reward)
        total_turns.append(info.get("turn", 0))
        
        if env.winner == args.player:
            wins += 1
    
    print(f"\n  Resultados ({n_eval} episódios):")
    print(f"  Vitórias: {wins}/{n_eval} ({wins/n_eval*100:.1f}%)")
    print(f"  Reward médio: {np.mean(total_rewards):+.2f} ± {np.std(total_rewards):.2f}")
    print(f"  Turnos médios: {np.mean(total_turns):.1f} ± {np.std(total_turns):.1f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Treinamento RL para OS Wars")
    subparsers = parser.add_subparsers(dest="command", help="Comando")
    
    # Subcomando: train
    train_parser = subparsers.add_parser("train", help="Treinar o agente")
    train_parser.add_argument("--player", type=str, default="Linux", 
                             choices=["Windows", "MacOS", "Linux"],
                             help="Nome do jogador RL (default: Linux)")
    train_parser.add_argument("--episodes", type=int, default=0,
                             help="Número de episódios (0 = infinito, Ctrl+C para parar) (default: 0)")
    train_parser.add_argument("--max-turns", type=int, default=200,
                             help="Máximo de turnos por episódio (default: 200)")
    train_parser.add_argument("--batch-size", type=int, default=64,
                             help="Tamanho do batch (default: 64)")
    train_parser.add_argument("--lr", type=float, default=1e-4,
                             help="Taxa de aprendizado (default: 1e-4)")
    train_parser.add_argument("--gamma", type=float, default=0.99,
                             help="Fator de desconto (default: 0.99)")
    train_parser.add_argument("--epsilon-start", type=float, default=1.0,
                             help="Epsilon inicial (default: 1.0)")
    train_parser.add_argument("--epsilon-end", type=float, default=0.05,
                             help="Epsilon final (default: 0.05)")
    train_parser.add_argument("--epsilon-decay", type=float, default=0.9995,
                             help="Decay do epsilon (default: 0.9995)")
    train_parser.add_argument("--target-update", type=int, default=1000,
                             help="Frequência de atualização da rede alvo (default: 1000)")
    train_parser.add_argument("--save-interval", type=int, default=500,
                             help="Intervalo de salvamento (default: 500 episódios)")
    train_parser.add_argument("--log-interval", type=int, default=50,
                             help="Intervalo de log (default: 50 episódios)")
    train_parser.add_argument("--resume", action="store_true",
                             help="Retomar treinamento do último checkpoint")
    
    # Subcomando: eval
    eval_parser = subparsers.add_parser("eval", help="Avaliar o agente")
    eval_parser.add_argument("--player", type=str, default="Linux",
                            choices=["Windows", "MacOS", "Linux"],
                            help="Nome do jogador RL (default: Linux)")
    eval_parser.add_argument("--eval-episodes", type=int, default=100,
                            help="Número de episódios de avaliação (default: 100)")
    eval_parser.add_argument("--max-turns", type=int, default=200,
                            help="Máximo de turnos por episódio (default: 200)")
    
    args = parser.parse_args()
    
    if args.command == "train":
        train(args)
    elif args.command == "eval":
        evaluate(args)
    else:
        # Default: train
        print("Uso: python train_rl.py {train|eval} [opções]")
        print("\nExemplos:")
        print("  python train_rl.py train --player Linux              (treina indefinidamente)")
        print("  python train_rl.py train --player Linux --episodes 5000  (treina 5000 episódios)")
        print("  python train_rl.py train --player Windows --resume   (retoma treinamento)")
        print("  python train_rl.py eval --player Linux               (avalia modelo treinado)")
        parser.print_help()
