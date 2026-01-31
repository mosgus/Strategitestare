# martingale.py
"""
    Martingale Betting Strategy CLI for American Roulette.
"""

import os
import sys

from game_engine import build_bet as bb
from strats import io as strat_io
from strats.strategies.martingale import run_martingale


def _slugify_label(label):
    return ''.join(c for c in label if c.isalnum() or c in ('-', '_'))


def main(argv=None):
    if argv is None:
        argv = sys.argv

    # Handle CLI arguments: python martingale.py <initial_balance> <buyout_profit> <optional_file> <optional_bet>
    try:
        if len(argv) >= 3:
            init_bal = float(argv[1])
            buy_prof = float(argv[2])
            seq_file = None
            bet_spec = None
            if len(argv) > 3:
                candidate = argv[3]
                if os.path.exists(candidate):
                    seq_file = candidate
                    bet_spec = argv[4] if len(argv) > 4 else None
                else:
                    bet_spec = candidate
        elif len(argv) == 2:
            init_bal = float(argv[1])
            buy_prof = float(input("Enter target profit (M): "))
            seq_file = None
            bet_spec = None
        else:
            init_bal = float(input("Enter initial balance (N): "))
            buy_prof = float(input("Enter target profit (M): "))
            print("\nExisting files in ../sequences/:", os.listdir('../sequences'))
            print("Example path to sequence CSV files:  ../sequences/roulette_sequence_100.csv")
            seq_file = input("\nEnter sequence CSV path (or press Enter for live): ").strip()
            if not seq_file:
                seq_file = None
            bet_spec = input("Enter bet spec (default red): ").strip()
            if not bet_spec:
                bet_spec = None

        outcomes = strat_io.load_sequence(seq_file)
        result = run_martingale(init_bal, buy_prof, bet_spec=bet_spec, outcomes=outcomes)

        print(f"\nStarting Martingale: Balance ${init_bal}, Target ${result['target_balance']} - 🟢")
        for row in result['rows']:
            if row.get('_all_in'):
                balance_str = row['Balance']
                print(f"Can't afford wager. Going all-in with ${balance_str} - 🟡")
            print(
                f"Round {row['Round']}: Bet on {row['Bet']} | "
                f"Landed on {row['Winning Number']} ({row['Color']}) | "
                f"Net: ${row['Net']} | Balance: ${row['Balance']}"
            )

        if result['outcome_label'] == "SUCCESS":
            print(f"{result['outcome_label']}: Hit buyout target in {result['round_count']} rounds! - 🔴")
        elif result['outcome_label'] == "DONE":
            print(f"{result['outcome_label']}: Reached end of sequence in {result['round_count']} rounds. - 🔴")
        else:
            print(f"{result['outcome_label']}: Bankroll hit zero in {result['round_count']} rounds. - 🔴")

        bet_label_for_file = bb.build_bet_from_spec(bet_spec, 1.0)[1]
        n_str = int(init_bal)
        m_str = int(buy_prof)
        bet_slug = _slugify_label(bet_label_for_file)
        filename = f"martingale_{n_str}n{m_str}m{bet_slug}.csv"

        out_dir = os.path.join(os.path.dirname(__file__), '..', 'strat_data')
        fieldnames = ['Round', 'Bet', 'Winning Number', 'Color', 'Net', 'Balance']
        path = strat_io.write_results(result['rows'], out_dir, filename, fieldnames)
        print(f"\nSaved results to {path}")
    except (ValueError, TypeError) as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
