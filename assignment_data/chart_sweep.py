import csv
from pathlib import Path

import matplotlib.pyplot as plt


def _load_rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _to_points(rows, x_key, y_key):
    points = []
    for row in rows:
        if x_key not in row and x_key == "M_profit" and "M" in row:
            x = float(row["M"])
        else:
            x = float(row[x_key])
        y = float(row[y_key])
        points.append((x, y))
    points.sort(key=lambda p: p[0])
    return points


def _plot_line(points, title, x_label, y_label, out_path):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    plt.figure(figsize=(10, 6))
    plt.plot(xs, ys, linewidth=2.0)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def _infer_iterations(rows):
    if not rows:
        return None
    sample = rows[0].get("Iterations")
    if sample is None:
        return None
    try:
        return int(float(sample))
    except ValueError:
        return None


def main():
    base_dir = Path(__file__).resolve().parent
    fixed_m_path = base_dir / "fixed_M_80_profit.csv"
    fixed_n_path = base_dir / "fixed_N_256_profit.csv"
    out_dir = base_dir / "charts"
    out_dir.mkdir(exist_ok=True)

    if not fixed_m_path.exists():
        candidates = sorted(base_dir.glob("fixed_M_*_*.csv"))
        if not candidates:
            raise FileNotFoundError(f"No fixed_M_*_*.csv files found in {base_dir}")
        fixed_m_path = candidates[-1]

    if not fixed_n_path.exists():
        candidates = sorted(base_dir.glob("fixed_N_*_*.csv"))
        if not candidates:
            raise FileNotFoundError(f"No fixed_N_*_*.csv files found in {base_dir}")
        fixed_n_path = candidates[-1]

    rows_fixed_m = _load_rows(fixed_m_path)
    rows_fixed_n = _load_rows(fixed_n_path)

    iterations = _infer_iterations(rows_fixed_m) or _infer_iterations(rows_fixed_n)
    iter_suffix = f" (Iterations: {iterations})" if iterations is not None else ""

    # 1) M fixed at 80: Prob_Win vs N
    pts = _to_points(rows_fixed_m, "N", "Prob_Win")
    _plot_line(
        pts,
        f"Probability of Winning vs N (M fixed at 80){iter_suffix}",
        "Initial Balance N ($)",
        "Probability of Winning",
        out_dir / "prob_win_vs_N_fixed_M80.png",
    )

    # 2) N fixed at 256: Prob_Win vs M
    pts = _to_points(rows_fixed_n, "M_profit", "Prob_Win")
    _plot_line(
        pts,
        f"Probability of Winning vs M (N fixed at 256){iter_suffix}",
        "Target Profit M ($)",
        "Probability of Winning",
        out_dir / "prob_win_vs_M_fixed_N256.png",
    )

    # 3) M fixed at 80: Expected Return vs N
    pts = _to_points(rows_fixed_m, "N", "Expected_Return")
    _plot_line(
        pts,
        f"Expected Return vs N (M fixed at 80){iter_suffix}",
        "Initial Balance N ($)",
        "Expected Return ($)",
        out_dir / "expected_return_vs_N_fixed_M80.png",
    )

    # 4) N fixed at 256: Expected Return vs M
    pts = _to_points(rows_fixed_n, "M_profit", "Expected_Return")
    _plot_line(
        pts,
        f"Expected Return vs M (N fixed at 256){iter_suffix}",
        "Target Profit M ($)",
        "Expected Return ($)",
        out_dir / "expected_return_vs_M_fixed_N256.png",
    )

    print(f"Saved charts to {out_dir}")


if __name__ == "__main__":
    main()
