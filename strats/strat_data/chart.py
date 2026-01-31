import csv
import os
from pathlib import Path
import matplotlib.pyplot as plt


def _read_runs(data_dir):
    runs = []
    # sorted() ensures the "last" file is consistent
    for path in sorted(Path(data_dir).glob("martingale_*.csv")):
        with path.open(newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        if not rows:
            continue
        runs.append((path.stem, rows))
    return runs


def _cumulative_win_rate(rows):
    wins = 0
    win_rates = []
    rounds = []
    for i, row in enumerate(rows, 1):
        net = float(row["Net"])
        if net > 0:
            wins += 1
        win_rates.append(wins / i)
        rounds.append(i)
    return rounds, win_rates


def _balance_curve(rows):
    rounds = []
    balances = []
    for i, row in enumerate(rows, 1):
        rounds.append(i)
        balances.append(float(row["Balance"]))
    return rounds, balances


def main():
    base_dir = Path(__file__).resolve().parent
    charts_dir = base_dir / "charts"
    charts_dir.mkdir(exist_ok=True)

    runs = _read_runs(base_dir)
    if not runs:
        print("No martingale_*.csv files found in directory.")
        return

    num_runs = len(runs)

    # OFFSET SETTINGS
    # Probability offset: small since range is only 0 to 1
    prob_offset_step = 0.004
    # Balance offset: slightly larger to be visible against high bankrolls
    bal_offset_step = 0.0

    # Chart 1: Cumulative win probability
    plt.figure(figsize=(12, 7))
    for i, (label, rows) in enumerate(runs):
        is_last = (i == num_runs - 1)
        x, y = _cumulative_win_rate(rows)

        # Apply Y-offset so lines don't perfectly overlap
        offset_y = [val + (i * prob_offset_step) for val in y]

        n = len(rows)
        marker = "o" if n < 15 else None

        plt.plot(
            x,
            offset_y,
            label=f"{label} ({n}r)" if not is_last else f"last: {label} ({n}r)",
            linewidth=3.0 if is_last else 2.5,
            alpha=1.0 if is_last else 0.6,
            marker=marker,
            markersize=2 if marker else 1,
            zorder=5000 if is_last else i,
            color="blue" if is_last else None
        )

    plt.title("Martingale Win Probability (Offset for Clarity)")
    plt.xlabel("Round")
    plt.ylabel("Win Probability (+ small offset)")
    plt.ylim(0, 1.2)
    plt.legend(fontsize=8, loc='upper right', bbox_to_anchor=(1.15, 1))
    plt.grid(True, alpha=0.2)
    win_path = charts_dir / "win_probability.png"
    plt.tight_layout()
    plt.savefig(win_path, dpi=150)
    plt.close()

    # Chart 2: Balance over time
    plt.figure(figsize=(12, 7))
    for i, (label, rows) in enumerate(runs):
        is_last = (i == num_runs - 1)
        x, y = _balance_curve(rows)

        # Apply Y-offset for balance
        offset_y = [val + (i * bal_offset_step) for val in y]

        n = len(rows)
        marker = "o" if n < 15 else None

        plt.plot(
            x,
            offset_y,
            label=f"{label} ({n}r)" if not is_last else f"LATEST: {label} ({n}r)",
            linewidth=2.5 if is_last else 1.5,
            alpha=1.0 if is_last else 0.5,
            marker=marker,
            markersize=2 if marker else 1,
            zorder=5000 if is_last else i,
            color="blue" if is_last else None
        )

    plt.title("Martingale Return Evolution")
    plt.xlabel("Round")
    plt.ylabel("Balance ($ + small offset)")
    plt.legend(fontsize=8, loc='upper right', bbox_to_anchor=(1.15, 1))
    plt.grid(True, alpha=0.2)
    bal_path = charts_dir / "balance.png"
    plt.tight_layout()
    plt.savefig(bal_path, dpi=150)
    plt.close()

    print(f"Analysis complete. Highlighted line: {runs[-1][0]}")
    print(f"Saved: {win_path}\nSaved: {bal_path}")


if __name__ == "__main__":
    main()