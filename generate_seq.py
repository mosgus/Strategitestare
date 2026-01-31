# generate_seq.py
"""
    Generates a sequence of roulette spins and saves them to a CSV file.

        input: number of spins (int)
        output: CSV file with columns [Round, Winning Number, Winning Index, Color]
"""

import sys
import csv
import os

from game_engine import build_bet as bb
from game_engine import roulette


def get_color(num):
    """Determines the color string based on the roulette number."""
    if num == '0' or num == '00':
        return 'Green'
    # Convert string num to int for set lookup
    n = int(num)
    if n in bb.RED_SET:
        return 'Red'
    if n in bb.BLACK_SET:
        return 'Black'
    return 'Unknown'


def generate_sequence(spins):
    filename = f"roulette_sequence_{spins}.csv"
    filepath = os.path.join('./sequences', filename)

    # We use a context manager to handle the CSV file creation
    os.makedirs('./sequences', exist_ok=True)
    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Round', 'Winning Number', 'Winning Index', 'Color']) # Write the header row

        for r in range(1, spins + 1):
            win_index = roulette.spin()
            win_num = roulette.index_to_num(win_index)
            color = get_color(win_num)
            writer.writerow([r, win_num, win_index, color])

    print(f"Successfully generated {spins} rolls in '{filepath}'.")


if __name__ == "__main__":
    # 1. Handle CLI Arguments or User Prompts
    if len(sys.argv) > 1:
        try:
            num_spins = int(sys.argv[1])
        except ValueError:
            print("Error: Please enter a valid integer for the number of spins.")
            sys.exit(1)
    else:
        try:
            num_spins = int(input("Enter quantity of rolls (max 100,000): "))
        except ValueError:
            print("Error: Input must be an integer.")
            sys.exit(1)

    # 2. Validation
    if num_spins > 100000:
        print("Limit exceeded. Setting spins to 100,000.")
        num_spins = 100000
    elif num_spins <= 0:
        print("Please enter a positive number.")
        sys.exit(1)

    # 3. Generate
    generate_sequence(num_spins)
