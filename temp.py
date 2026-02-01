# temp.py
import argparse
import csv
import os
import random
import time

from strats import io as strat_io
from strats.martingale import run_martingale


def simulate_point(n, m_profit, iterations, bet_spec='red', seed_base=None, outcomes=None):
    wins = 0
    total_return = 0.0

    for i in range(iterations):
        rng = None
        if outcomes is None and seed_base is not None:
            rng = random.Random(seed_base + i)
        result = run_martingale(n, m_profit, bet_spec=bet_spec, outcomes=outcomes, rng=rng)
        if result['outcome_label'] == 'SUCCESS':
            wins += 1
        total_return += (result['final_balance'] - n)

    prob_win = wins / iterations if iterations else 0.0
    expected_return = total_return / iterations if iterations else 0.0
    return wins, prob_win, expected_return


def _parse_values_list(values_arg):
    if not values_arg:
        return None
    parts = [p.strip() for p in values_arg.replace(',', ' ').split()]
    values = []
    for part in parts:
        if not part:
            continue
        values.append(int(part))
    return values or None


def _resolve_buyout(n, m_value, m_mode):
    if m_mode == 'target_balance':
        return m_value - n
    return m_value


def run_assignment(
    n_min,
    n_max,
    n_step,
    m_min,
    m_max,
    m_step,
    iterations,
    bet_spec,
    seed_base,
    sequence_path,
    fixed_m,
    fixed_n,
    n_values,
    m_values,
    m_mode,
    progress,
    progress_every,
):
    os.makedirs('assignment_data', exist_ok=True)
    outcomes = strat_io.load_sequence(sequence_path) if sequence_path else None
    if outcomes and iterations > 1:
        print("Note: sequence replay is deterministic; iterations > 1 will repeat identical runs.")

    n_sweep = n_values or list(range(n_min, n_max + 1, n_step))
    m_sweep = m_values or list(range(m_min, m_max + 1, m_step))

    # Scenario 1 & 3: Fixed M (profit target), N from n_min to n_max
    results_n = []
    total_points = len(n_sweep) + len(m_sweep)
    point_index = 0
    start_time = time.time()
    for n in n_sweep:
        point_index += 1
        buyout = _resolve_buyout(n, fixed_m, m_mode)
        wins, prob, exp = simulate_point(
            n,
            buyout,
            iterations,
            bet_spec=bet_spec,
            seed_base=seed_base,
            outcomes=outcomes,
        )
        results_n.append({
            'N': n,
            'M_profit': fixed_m,
            'Wins': wins,
            'Iterations': iterations,
            'Prob_Win': f"{prob:.6f}",
            'Expected_Return': f"{exp:.6f}",
        })
        if progress and (point_index % progress_every == 0 or point_index == total_points):
            elapsed = time.time() - start_time
            msg = f"[{point_index}/{total_points}] N={n} M={fixed_m} elapsed={elapsed:.1f}s"
            print(msg, end="\r", flush=True)

    # Scenario 2 & 4: Fixed N, M (profit target) from m_min to m_max
    results_m = []
    for m_profit in m_sweep:
        point_index += 1
        buyout = _resolve_buyout(fixed_n, m_profit, m_mode)
        wins, prob, exp = simulate_point(
            fixed_n,
            buyout,
            iterations,
            bet_spec=bet_spec,
            seed_base=seed_base,
            outcomes=outcomes,
        )
        results_m.append({
            'N': fixed_n,
            'M_profit': m_profit,
            'Wins': wins,
            'Iterations': iterations,
            'Prob_Win': f"{prob:.6f}",
            'Expected_Return': f"{exp:.6f}",
        })
        if progress and (point_index % progress_every == 0 or point_index == total_points):
            elapsed = time.time() - start_time
            msg = f"[{point_index}/{total_points}] N={fixed_n} M={m_profit} elapsed={elapsed:.1f}s"
            print(msg, end="\r", flush=True)

    suffix = "target_balance" if m_mode == 'target_balance' else "profit"
    with open(f'assignment_data/fixed_M_{fixed_m}_{suffix}.csv', 'w', newline='') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=['N', 'M_profit', 'Wins', 'Iterations', 'Prob_Win', 'Expected_Return'],
        )
        writer.writeheader()
        writer.writerows(results_n)

    with open(f'assignment_data/fixed_N_{fixed_n}_{suffix}.csv', 'w', newline='') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=['N', 'M_profit', 'Wins', 'Iterations', 'Prob_Win', 'Expected_Return'],
        )
        writer.writeheader()
        writer.writerows(results_m)

    if progress:
        print()
    print("Assignment data saved to /assignment_data")


def parse_args():
    parser = argparse.ArgumentParser(description="Generate assignment data for martingale strategy.")  # CLI config
    parser.add_argument('--n-min', type=int, default=1)  # N sweep start (initial bankroll)
    parser.add_argument('--n-max', type=int, default=1000)  # N sweep end (initial bankroll)
    parser.add_argument('--n-step', type=int, default=10)  # N sweep increment
    parser.add_argument('--m-min', type=int, default=1)  # M sweep start (net profit target)
    parser.add_argument('--m-max', type=int, default=1000)  # M sweep end (net profit target)
    parser.add_argument('--m-step', type=int, default=10)  # M sweep increment
    parser.add_argument('--iterations', type=int, default=5)  # Runs per (N, M); increase for smoother probabilities.
    parser.add_argument('--bet', type=str, default='red')  # Bet spec for each run
    parser.add_argument('--seed-base', type=int, default=None)  # Base RNG seed for reproducible runs
    parser.add_argument('--sequence-path', type=str, default=None)  # Optional sequence CSV to replay
    parser.add_argument('--fixed-m', type=int, default=80)  # Fixed profit target for M-sweep scenarios
    parser.add_argument('--fixed-n', type=int, default=256)  # Fixed initial bankroll for N-sweep scenarios
    parser.add_argument('--n-values', type=str, default=None)  # Comma/space-separated N values override
    parser.add_argument('--m-values', type=str, default=None)  # Comma/space-separated M values override
    parser.add_argument(
        '--m-mode',
        type=str,
        default='profit',
        choices=['profit', 'target_balance'],
    )  # Interpret M as profit or target balance
    parser.add_argument('--progress', action='store_true')  # Print progress as points finish
    parser.add_argument('--progress-every', type=int, default=100)  # Progress print interval
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_assignment(
        n_min=args.n_min,
        n_max=args.n_max,
        n_step=args.n_step,
        m_min=args.m_min,
        m_max=args.m_max,
        m_step=args.m_step,
        iterations=args.iterations,
        bet_spec=args.bet,
        seed_base=args.seed_base,
        sequence_path=args.sequence_path,
        fixed_m=args.fixed_m,
        fixed_n=args.fixed_n,
        n_values=_parse_values_list(args.n_values),
        m_values=_parse_values_list(args.m_values),
        m_mode=args.m_mode,
        progress=args.progress,
        progress_every=max(1, args.progress_every),
    )
