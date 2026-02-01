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


def _plot_combo(
    points_a,
    label_a,
    points_b,
    label_b,
    title,
    x_label,
    y_label,
    out_path,
):
    xa = [p[0] for p in points_a]
    ya = [p[1] for p in points_a]
    xb = [p[0] for p in points_b]
    yb = [p[1] for p in points_b]

    plt.figure(figsize=(10, 6))
    plt.plot(xa, ya, linewidth=2.0, label=label_a)
    plt.plot(xb, yb, linewidth=2.0, label=label_b)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.grid(True, alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


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

    # Combined Prob_Win chart
    pts_prob_fixed_m = _to_points(rows_fixed_m, "N", "Prob_Win")
    pts_prob_fixed_n = _to_points(rows_fixed_n, "M_profit", "Prob_Win")
    _plot_combo(
        pts_prob_fixed_m,
        "M fixed at 80 (x = N)",
        pts_prob_fixed_n,
        "N fixed at 256 (x = M)",
        f"Probability of Winning (Fixed M vs Fixed N){iter_suffix}",
        "N or M ($)",
        "Probability of Winning",
        out_dir / "prob_win_combo_fixedM_fixedN.png",
    )

    # Combined Expected Return chart
    pts_ret_fixed_m = _to_points(rows_fixed_m, "N", "Expected_Return")
    pts_ret_fixed_n = _to_points(rows_fixed_n, "M_profit", "Expected_Return")
    _plot_combo(
        pts_ret_fixed_m,
        "M fixed at 80 (x = N)",
        pts_ret_fixed_n,
        "N fixed at 256 (x = M)",
        f"Expected Return (Fixed M vs Fixed N){iter_suffix}",
        "N or M ($)",
        "Expected Return ($)",
        out_dir / "expected_return_combo_fixedM_fixedN.png",
    )

    print(f"Saved combo charts to {out_dir}")


if __name__ == "__main__":
    main()
