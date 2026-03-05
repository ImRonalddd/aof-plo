"""
Run the CFR+ solver and export strategies to ranges.json.

Usage:
    cd solver && source .venv/Scripts/activate
    python src/export.py                    # quick dev run (5k iters)
    python src/export.py --iters 50000 --equity 1000  # production run
"""

import json
import time
import sys
import argparse
from pathlib import Path

# Allow running as script from solver/ or solver/src/ dir
sys.path.insert(0, str(Path(__file__).parent))

from cfr import CFRSolver


def run_and_export(
    n_iterations: int = 5_000,
    equity_samples: int = 200,
    output_path: str | None = None,
    seed: int = 42,
) -> Path:
    if output_path is None:
        # Default: write to web/public/ranges.json relative to repo root
        repo_root = Path(__file__).parent.parent.parent
        output_path = str(repo_root / "web" / "public" / "ranges.json")

    print(f"CFR+ solver: {n_iterations:,} iterations, {equity_samples} equity samples")
    start = time.time()

    solver = CFRSolver(n_players=4, equity_samples=equity_samples)
    solver.train(n_iterations=n_iterations, seed=seed)

    elapsed = time.time() - start
    print(f"Training done in {elapsed:.1f}s — {len(solver.infosets):,} infosets")

    # Serialize: convert numpy arrays to plain lists
    strategies = {
        k: v.tolist()
        for k, v in solver.get_average_strategies().items()
    }

    output = {
        "meta": {
            "iterations": n_iterations,
            "equity_samples": equity_samples,
            "n_infosets": len(strategies),
            "elapsed_seconds": round(elapsed, 1),
        },
        "strategies": strategies,
    }

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump(output, f, separators=(",", ":"))

    size_kb = out.stat().st_size / 1000
    print(f"Wrote {out} ({size_kb:.0f} KB)")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="AOF PLO CFR+ solver")
    parser.add_argument("--iters", type=int, default=5_000)
    parser.add_argument("--equity", type=int, default=200)
    parser.add_argument("--output", type=str, default=None)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    run_and_export(
        n_iterations=args.iters,
        equity_samples=args.equity,
        output_path=args.output,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
