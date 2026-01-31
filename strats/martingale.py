# martingale.py
"""
    Martingale Betting Strategy Implementation for American Roulette:

        input: initial_balance (float), buyout_profit (float), optional_sequence_file (str)
        output: Game Summary
"""

# martingale.py
import sys
import csv
import os
from game_engine import build_bet as bb
from game_engine import roulette


def run_martingale(initial_balance, buyout, sequence_path=None):
    balance = initial_balance
    target_balance = initial_balance + buyout
    current_wager = 1.0
    round_count = 0

    # Optional: Load sequence data if a file path is provided
    outcomes = []
    if sequence_path and os.path.exists(sequence_path):
        with open(sequence_path, 'r') as f:
            reader = csv.DictReader(f)
            outcomes = list(reader)

    max_rounds = len(outcomes) if outcomes else None

    print(f"--- Starting Martingale: Balance ${balance}, Target ${target_balance} ---")

    while 0 < balance < target_balance and (max_rounds is None or round_count < max_rounds):
        round_count += 1

        # 1. Check if we can afford the current wager
        if current_wager > balance:
            print(f"Cannot afford wager of ${current_wager}. Going all-in with ${balance}.")
            current_wager = balance

        # 2. Construct the bet (Using 'Red' as a standard even-money bet)
        bet_array = bb.bet_red(current_wager)

        # 3. Get the winning index (From file or live RNG)
        if outcomes and (round_count - 1) < len(outcomes):
            row = outcomes[round_count - 1]
            win_index = int(row['Winning Index'])
            win_label = row['Winning Number']
            color = row['Color']
        else:
            win_index = roulette.spin()
            win_label = roulette.index_to_num(win_index)
            color = roulette.num_to_color(win_label)

        # 4. Calculate Payout
        net_result = roulette.payout(bet_array, win_index)
        balance += net_result

        print(f"Round {round_count}: Landed on {win_label} ({color}) | Net: ${net_result:+.2f} | Balance: ${balance:.2f}")

        # 5. Martingale Logic: Double on loss, reset on win
        if net_result > 0:
            current_wager = 1.0  # Reset
        else:
            current_wager *= 2  # Double down

    # Termination Summary
    if balance >= target_balance:
        print(f"--- SUCCESS: Hit buyout target in {round_count} rounds! ---")
    elif max_rounds is not None and round_count >= max_rounds:
        print(f"--- DONE: Reached end of sequence in {round_count} rounds. ---")
    else:
        print(f"--- BUST: Bankroll hit zero in {round_count} rounds. ---")


if __name__ == "__main__":
    # Handle CLI arguments: python martingale.py <initial_balance> <buyout_profit> <optional_file>
    try:
        if len(sys.argv) >= 3:
            init_bal = float(sys.argv[1])
            buy_prof = float(sys.argv[2])
            seq_file = sys.argv[3] if len(sys.argv) > 3 else None
        elif len(sys.argv) == 2:
            init_bal = float(sys.argv[1])
            buy_prof = float(input("Enter target profit (M): "))
            seq_file = None
        else:
            init_bal = float(input("Enter initial balance (N): "))
            buy_prof = float(input("Enter target profit (M): "))
            print("\nExisting files in ../sequences/:", os.listdir('../sequences'))
            print("Example path to sequence CSV files:  ../sequences/roulette_sequence_100.csv")
            seq_file = input("\nEnter sequence CSV path (or press Enter for live): ").strip()
            if not seq_file: seq_file = None

        run_martingale(init_bal, buy_prof, seq_file)
    except ValueError:
        print("Error: Please provide numeric values for balance and profit.")
