"""
    Core martingale strategy logic (no file I/O).
"""

from game_engine import build_bet as bb
from game_engine import roulette


def run_martingale(initial_balance, buyout, bet_spec=None, outcomes=None, rng=None):
    balance = initial_balance
    if buyout > initial_balance:
        target_balance = buyout
    else:
        target_balance = initial_balance + buyout
    current_wager = 1.0
    round_count = 0
    rows = []

    max_rounds = len(outcomes) if outcomes else None

    while 0 < balance < target_balance and (max_rounds is None or round_count < max_rounds):
        round_count += 1

        # 1. Check if we can afford the current wager
        all_in = False
        if current_wager > balance:
            current_wager = balance
            all_in = True

        # 2. Construct the bet
        bet_array, bet_label = bb.build_bet_from_spec(bet_spec, current_wager)

        # 3. Get the winning index (From file or live RNG)
        if outcomes and (round_count - 1) < len(outcomes):
            row = outcomes[round_count - 1]
            win_index = int(row['Winning Index'])
            win_label = row['Winning Number']
            color = row.get('Color') or roulette.num_to_color(win_label)
        else:
            win_index = roulette.spin(rng=rng)
            win_label = roulette.index_to_num(win_index)
            color = roulette.num_to_color(win_label)

        # 4. Calculate Payout
        net_result = roulette.payout(bet_array, win_index)
        balance += net_result

        # 5. Martingale Logic: Double on loss, reset on win
        if net_result > 0:
            current_wager = 1.0  # Reset
        else:
            current_wager *= 2  # Double down

        rows.append({
            'Round': round_count,
            'Bet': bet_label,
            'Winning Number': win_label,
            'Color': color,
            'Net': f"{net_result:+.2f}",
            'Balance': f"{balance:.2f}",
            '_net_raw': net_result,
            '_all_in': all_in,
        })

    # Termination Summary
    if balance >= target_balance:
        outcome_label = "SUCCESS"
    elif max_rounds is not None and round_count >= max_rounds:
        outcome_label = "DONE"
    else:
        outcome_label = "BUST"

    return {
        'rows': rows,
        'round_count': round_count,
        'outcome_label': outcome_label,
        'target_balance': target_balance,
        'final_balance': balance,
    }
