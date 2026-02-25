#!/usr/bin/env python3
"""
OS Wars — Pipeline completo de treinamento RL para os 3 sistemas operacionais.

Fase 1: Treina cada SO individualmente contra IA aleatória (warm-up).
Fase 2: Self-play — cada SO treina jogando contra os outros dois modelos RL.
         Roda indefinidamente até Ctrl+C.

Uso:
    python train_all.py                 # Roda tudo com defaults
    python train_all.py --phase1 3000   # 3000 episódios na fase 1 por SO
    python train_all.py --skip-phase1   # Pula direto para self-play (precisa de modelos salvos)
    python train_all.py --phase1 0      # Equivalente a --skip-phase1
"""

import os
import sys
import time
import signal
import argparse
import json
from datetime import datetime, timedelta

import numpy as np

# ─── PyTorch ────────────────────────────────────────────────────────────────
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    print("ERRO: PyTorch não encontrado. Instale com:")
    print("  pip install --pre torch --index-url https://download.pytorch.org/whl/nightly/cu128")
    sys.exit(1)

# ─── Projeto ────────────────────────────────────────────────────────────────
from game.rl.rl_agent import RLAgent, ACTION_SPACE, NUM_ACTIONS, STATE_DIM
from game.rl.environment import OSWarsEnv
from game.utils.constants import PLAYERS

# ─── Constantes do treinamento ──────────────────────────────────────────────
DEFAULT_PHASE1_EPISODES = 2500      # Episódios contra IA aleatória por SO
DEFAULT_MAX_TURNS = 200             # Turnos máximos por episódio
SAVE_INTERVAL = 200                 # Salva modelo a cada N episódios
LOG_INTERVAL = 50                   # Imprime métricas a cada N episódios
EVAL_GAMES = 30                     # Jogos de avaliação entre fases
MODELS_DIR = "models"

# ─── Interrupção graciosa ───────────────────────────────────────────────────
_stop_requested = False

def _signal_handler(sig, frame):
    global _stop_requested
    if _stop_requested:
        print("\n\nSegunda interrupção — saindo imediatamente.")
        sys.exit(1)
    _stop_requested = True
    print("\n\n⏸  Ctrl+C detectado — finalizando episódio atual e salvando modelos...")

signal.signal(signal.SIGINT, _signal_handler)


# ═══════════════════════════════════════════════════════════════════════════
# Utilitários
# ═══════════════════════════════════════════════════════════════════════════

def print_header(title: str):
    w = 70
    print()
    print("═" * w)
    print(f"  {title}")
    print("═" * w)


def print_device_info():
    if torch.cuda.is_available():
        gpu = torch.cuda.get_device_name(0)
        mem = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
        print(f"  Device : CUDA — {gpu} ({mem:.1f} GB)")
    else:
        print("  Device : CPU")


def fmt_time(seconds: float) -> str:
    return str(timedelta(seconds=int(seconds)))


def ensure_models_dir():
    os.makedirs(MODELS_DIR, exist_ok=True)


def save_metrics(metrics: dict, filename: str):
    path = os.path.join(MODELS_DIR, filename)
    with open(path, "w") as f:
        json.dump(metrics, f, indent=2)


# ═══════════════════════════════════════════════════════════════════════════
# Fase 1 — Treinamento contra IA aleatória (warm-up)
# ═══════════════════════════════════════════════════════════════════════════

def train_vs_random(os_name: str, episodes: int, max_turns: int, resume: bool = True) -> dict:
    """
    Treina um SO contra 2 IAs aleatórias.
    Retorna dicionário com métricas.
    """
    global _stop_requested

    print_header(f"FASE 1 — {os_name} vs IA Aleatória ({episodes} episódios)")

    agent = RLAgent(os_name, training=True)
    if resume:
        agent.load_model()

    env = OSWarsEnv(rl_player_name=os_name, max_turns=max_turns)

    rewards_history = []
    wins = 0
    total_episodes = 0
    t0 = time.time()

    for ep in range(1, episodes + 1):
        if _stop_requested:
            break

        state = env.reset()
        episode_reward = 0
        done = False

        while not done:
            valid_mask = env.get_valid_actions()
            action = agent.select_action(state, valid_mask)
            next_state, reward, done, info = env.step(action)
            agent.store_transition(state, action, reward, next_state, done)
            agent.train_step()
            episode_reward += reward
            state = next_state

        agent.end_episode(episode_reward)
        total_episodes += 1
        rewards_history.append(episode_reward)

        if info.get("winner") == os_name:
            wins += 1

        # Log
        if ep % LOG_INTERVAL == 0:
            recent = rewards_history[-LOG_INTERVAL:]
            avg_r = np.mean(recent)
            win_rate = wins / total_episodes * 100
            eps = agent.epsilon
            elapsed = time.time() - t0
            speed = total_episodes / elapsed if elapsed > 0 else 0
            print(
                f"  [{os_name}] Ep {ep:>5}/{episodes} | "
                f"R̄={avg_r:>7.1f} | Win={win_rate:>5.1f}% | "
                f"ε={eps:.3f} | {speed:.1f} ep/s | {fmt_time(elapsed)}"
            )

        # Salvar
        if ep % SAVE_INTERVAL == 0:
            agent.save_model()

    # Salvar final
    agent.save_model()
    elapsed = time.time() - t0
    win_rate = wins / max(total_episodes, 1) * 100

    print(f"\n  ✓ {os_name}: {total_episodes} episódios, "
          f"Win rate={win_rate:.1f}%, Tempo={fmt_time(elapsed)}")

    return {
        "os": os_name,
        "episodes": total_episodes,
        "win_rate": win_rate,
        "avg_reward": float(np.mean(rewards_history)) if rewards_history else 0,
        "time_seconds": elapsed,
        "epsilon_final": agent.epsilon,
    }


# ═══════════════════════════════════════════════════════════════════════════
# Avaliação rápida (round-robin)
# ═══════════════════════════════════════════════════════════════════════════

def evaluate_round_robin(num_games: int, max_turns: int) -> dict:
    """Cada SO joga num_games como protagonista contra os outros dois RL."""
    print_header(f"AVALIAÇÃO — Round-Robin ({num_games} jogos por SO)")

    # Carrega todos os agentes (modo inferência)
    agents = {}
    for name in PLAYERS:
        a = RLAgent(name)
        a.load_model()
        a.epsilon = 0.0  # greedy
        agents[name] = a

    results = {name: {"wins": 0, "games": 0} for name in PLAYERS}

    for protagonist in PLAYERS:
        opponents = {p: agents[p] for p in PLAYERS if p != protagonist}
        env = OSWarsEnv(
            rl_player_name=protagonist,
            max_turns=max_turns,
            opponent_agents=opponents,
        )

        for g in range(num_games):
            state = env.reset()
            done = False
            while not done:
                valid_mask = env.get_valid_actions()
                action = agents[protagonist].select_action(state, valid_mask)
                state, _, done, info = env.step(action)

            results[protagonist]["games"] += 1
            if info.get("winner") == protagonist:
                results[protagonist]["wins"] += 1

    print()
    for name in PLAYERS:
        w = results[name]["wins"]
        g = results[name]["games"]
        wr = w / g * 100 if g else 0
        print(f"  {name:>8}: {w}/{g} vitórias ({wr:.1f}%)")

    return results


# ═══════════════════════════════════════════════════════════════════════════
# Fase 2 — Self-play (RL vs RL vs RL)
# ═══════════════════════════════════════════════════════════════════════════

def train_self_play(max_turns: int):
    """
    Treina os 3 SOs em self-play round-robin contínuo.
    Cada "rodada" treina cada SO por um bloco de episódios contra os outros dois RL,
    depois atualiza os oponentes com os novos pesos.
    Roda até Ctrl+C.
    """
    global _stop_requested

    print_header("FASE 2 — Self-Play (RL vs RL vs RL) — Ctrl+C para parar")

    # Carrega agentes (modo treinamento)
    agents = {}
    for name in PLAYERS:
        a = RLAgent(name, training=True)
        a.load_model()
        agents[name] = a
        print(f"  {name}: ε={a.epsilon:.4f}, modelo carregado")

    BLOCK_SIZE = 100  # episódios por SO por rodada
    round_num = 0
    total_episodes = {name: 0 for name in PLAYERS}
    total_wins = {name: 0 for name in PLAYERS}
    t0 = time.time()

    while not _stop_requested:
        round_num += 1
        round_t0 = time.time()

        for protagonist in PLAYERS:
            if _stop_requested:
                break

            # Oponentes: cópias dos modelos atuais (frozen, greedy)
            opponent_agents = {}
            for opp_name in PLAYERS:
                if opp_name != protagonist:
                    opp = RLAgent(opp_name)
                    # Copia pesos do agente treinado
                    opp.policy_net.load_state_dict(agents[opp_name].policy_net.state_dict())
                    opp.target_net.load_state_dict(agents[opp_name].target_net.state_dict())
                    opp.epsilon = 0.05  # pequena exploração para variedade
                    opponent_agents[opp_name] = opp

            env = OSWarsEnv(
                rl_player_name=protagonist,
                max_turns=max_turns,
                opponent_agents=opponent_agents,
            )

            block_rewards = []
            block_wins = 0

            for ep in range(BLOCK_SIZE):
                if _stop_requested:
                    break

                state = env.reset()
                episode_reward = 0
                done = False

                while not done:
                    valid_mask = env.get_valid_actions()
                    action = agents[protagonist].select_action(state, valid_mask)
                    next_state, reward, done, info = env.step(action)
                    agents[protagonist].store_transition(state, action, reward, next_state, done)
                    agents[protagonist].train_step()
                    episode_reward += reward
                    state = next_state

                agents[protagonist].end_episode(episode_reward)
                block_rewards.append(episode_reward)
                total_episodes[protagonist] += 1

                if info.get("winner") == protagonist:
                    block_wins += 1
                    total_wins[protagonist] += 1

            # Estatísticas do bloco
            avg_r = np.mean(block_rewards) if block_rewards else 0
            eps = agents[protagonist].epsilon
            cumulative_wr = (
                total_wins[protagonist] / total_episodes[protagonist] * 100
                if total_episodes[protagonist] > 0 else 0
            )
            print(
                f"  R{round_num:>3} [{protagonist:>8}] "
                f"+{len(block_rewards)} ep | R̄={avg_r:>7.1f} | "
                f"Blk Win={block_wins}/{len(block_rewards)} | "
                f"Total Win={cumulative_wr:>5.1f}% | ε={eps:.4f}"
            )

        # Salvar todos os modelos no fim de cada rodada
        for name in PLAYERS:
            agents[name].save_model()

        round_elapsed = time.time() - round_t0
        total_elapsed = time.time() - t0
        total_ep = sum(total_episodes.values())
        speed = total_ep / total_elapsed if total_elapsed > 0 else 0
        print(
            f"  ── Rodada {round_num} concluída em {fmt_time(round_elapsed)} | "
            f"Total: {total_ep} ep em {fmt_time(total_elapsed)} ({speed:.1f} ep/s)"
        )
        print()

    # Salvar final
    print("\nSalvando modelos finais...")
    for name in PLAYERS:
        agents[name].save_model()

    # Métricas finais
    elapsed = time.time() - t0
    print_header("SELF-PLAY — Resumo Final")
    for name in PLAYERS:
        ep = total_episodes[name]
        w = total_wins[name]
        wr = w / ep * 100 if ep > 0 else 0
        print(f"  {name:>8}: {ep} episódios, {w} vitórias ({wr:.1f}%), ε={agents[name].epsilon:.4f}")
    print(f"\n  Tempo total: {fmt_time(elapsed)} | Rodadas: {round_num}")

    # Salva métricas
    save_metrics({
        "phase": "self_play",
        "rounds": round_num,
        "total_time": elapsed,
        "players": {
            name: {
                "episodes": total_episodes[name],
                "wins": total_wins[name],
                "win_rate": total_wins[name] / max(total_episodes[name], 1) * 100,
                "epsilon": agents[name].epsilon,
            }
            for name in PLAYERS
        },
    }, "selfplay_metrics.json")


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

def main():
    global _stop_requested

    parser = argparse.ArgumentParser(
        description="OS Wars — Treinamento completo RL (warm-up + self-play)"
    )
    parser.add_argument(
        "--phase1", type=int, default=DEFAULT_PHASE1_EPISODES,
        help=f"Episódios da Fase 1 por SO (default: {DEFAULT_PHASE1_EPISODES}). Use 0 para pular."
    )
    parser.add_argument(
        "--skip-phase1", action="store_true",
        help="Pula Fase 1 e vai direto para self-play (requer modelos já treinados)."
    )
    parser.add_argument(
        "--max-turns", type=int, default=DEFAULT_MAX_TURNS,
        help=f"Turnos máximos por episódio (default: {DEFAULT_MAX_TURNS})."
    )
    parser.add_argument(
        "--no-eval", action="store_true",
        help="Pula avaliação round-robin entre fases."
    )
    args = parser.parse_args()

    skip_phase1 = args.skip_phase1 or args.phase1 == 0

    # ─── Banner ─────────────────────────────────────────────────────────
    print_header("OS WARS — TREINAMENTO RL COMPLETO")
    print_device_info()
    print(f"  Fase 1  : {'SKIP' if skip_phase1 else f'{args.phase1} episódios/SO'}")
    print(f"  Fase 2  : Self-play infinito (Ctrl+C para parar)")
    print(f"  Max turns: {args.max_turns}")
    print(f"  Modelos  : {os.path.abspath(MODELS_DIR)}/")
    print(f"  Início   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    ensure_models_dir()
    global_t0 = time.time()

    # ─── Fase 1 ─────────────────────────────────────────────────────────
    if not skip_phase1:
        phase1_metrics = []
        for os_name in PLAYERS:
            if _stop_requested:
                break
            metrics = train_vs_random(os_name, args.phase1, args.max_turns)
            phase1_metrics.append(metrics)

        save_metrics({"phase1": phase1_metrics}, "phase1_metrics.json")

        # Avaliação intermediária
        if not args.no_eval and not _stop_requested:
            evaluate_round_robin(EVAL_GAMES, args.max_turns)
    else:
        # Verifica se modelos existem
        missing = []
        for name in PLAYERS:
            path = os.path.join(MODELS_DIR, f"rl_agent_{name.lower()}.pth")
            if not os.path.exists(path):
                missing.append(name)
        if missing:
            print(f"\n  AVISO: Modelos não encontrados para: {', '.join(missing)}")
            print("  Serão inicializados com pesos aleatórios.\n")

    # ─── Fase 2 ─────────────────────────────────────────────────────────
    if not _stop_requested:
        _stop_requested = False  # Reset flag para permitir Ctrl+C na fase 2
        train_self_play(args.max_turns)

    # ─── Fim ────────────────────────────────────────────────────────────
    total_time = time.time() - global_t0
    print_header("TREINAMENTO CONCLUÍDO")
    print(f"  Tempo total: {fmt_time(total_time)}")
    print(f"  Modelos salvos em: {os.path.abspath(MODELS_DIR)}/")
    print()


if __name__ == "__main__":
    main()
