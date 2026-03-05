"""
Run the CFR+ solver and export strategies to ranges.json.

Supports time-based runs with checkpoint save/resume.

Usage:
    cd solver && source .venv/Scripts/activate

    # Run for 1 hour (default), auto-save checkpoint every 5 min:
    python src/export.py

    # Resume a previous run for another 30 minutes:
    python src/export.py --duration 1800

    # Custom options:
    python src/export.py --duration 3600 --equity 500 --checkpoint solver/checkpoint.pkl

Ctrl+C at any time saves the checkpoint and exports current ranges.json.
"""

import json
import os
import signal
import sys
import time
import argparse
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cfr import CFRSolver

REPO_ROOT = Path(__file__).parent.parent.parent
DEFAULT_CHECKPOINT = str(REPO_ROOT / "solver" / "checkpoint.pkl")
DEFAULT_OUTPUT = str(REPO_ROOT / "web" / "public" / "ranges.json")

# Will be set to True by the signal handler on Ctrl+C
_stop_requested = False


def _handle_sigint(sig, frame):
    global _stop_requested
    if not _stop_requested:
        print("\n\nCtrl+C received — finishing current iteration then saving...")
        _stop_requested = True


def write_ranges_json(solver: CFRSolver, iteration: int, equity_samples: int,
                      elapsed: float, output_path: str) -> None:
    strategies = {
        k: v.tolist()
        for k, v in solver.get_average_strategies().items()
    }
    output = {
        "meta": {
            "iterations": iteration,
            "equity_samples": equity_samples,
            "n_infosets": len(strategies),
            "elapsed_seconds": round(elapsed, 1),
        },
        "strategies": strategies,
    }
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = str(out) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(output, f, separators=(",", ":"))
    os.replace(tmp, str(out))
    size_kb = out.stat().st_size / 1000
    print(f"  -> Wrote {out.name} ({size_kb:.0f} KB, {len(strategies):,} infosets)")


def run_timed(
    duration_seconds: int = 3600,
    equity_samples: int = 500,
    checkpoint_path: str = DEFAULT_CHECKPOINT,
    output_path: str = DEFAULT_OUTPUT,
    save_interval: int = 300,   # checkpoint every 5 minutes
    report_interval: int = 100, # print progress every N iterations
    seed: int = 42,
) -> None:
    global _stop_requested

    signal.signal(signal.SIGINT, _handle_sigint)

    # --- Load or init solver ---
    ckpt = Path(checkpoint_path)
    if ckpt.exists():
        print(f"Resuming from checkpoint: {ckpt}")
        solver, start_iter, rng_state = CFRSolver.load_checkpoint(checkpoint_path)
        rng = random.Random()
        rng.setstate(rng_state)
        print(f"  Loaded {len(solver.infosets):,} infosets, "
              f"continuing from iteration {start_iter + 1}")
    else:
        print("No checkpoint found — starting fresh")
        solver = CFRSolver(n_players=4, equity_samples=equity_samples)
        rng = random.Random(seed)
        start_iter = 0

    reach = __import__("numpy").ones(4)

    print(f"\nRunning for {duration_seconds // 60} min "
          f"({duration_seconds}s) · {equity_samples} equity samples/iter")
    print(f"Checkpoint: {ckpt}")
    print(f"Output:     {output_path}")
    print(f"Press Ctrl+C to pause and save at any time.\n")

    run_start = time.time()
    last_save = run_start
    t = start_iter
    iter_times: list[float] = []

    while True:
        if _stop_requested:
            break

        elapsed_run = time.time() - run_start
        if elapsed_run >= duration_seconds:
            print(f"\nTime limit reached ({duration_seconds}s).")
            break

        # --- One CFR+ iteration ---
        iter_start = time.time()
        t += 1
        hands = solver._deal_hands(rng)
        solver._cfr("", hands, reach.copy(), iteration=t)
        iter_times.append(time.time() - iter_start)

        # --- Progress report ---
        if t % report_interval == 0:
            elapsed_total = time.time() - run_start
            avg_iter = sum(iter_times[-report_interval:]) / len(iter_times[-report_interval:])
            iters_per_sec = 1.0 / avg_iter if avg_iter > 0 else 0
            remaining = duration_seconds - elapsed_total
            eta_iters = int(remaining * iters_per_sec)
            print(
                f"  iter {t:>7,} | "
                f"elapsed {elapsed_total:>6.0f}s | "
                f"{iters_per_sec:.2f} iter/s | "
                f"~{eta_iters:,} iters remaining | "
                f"{len(solver.infosets):,} infosets"
            )

        # --- Periodic checkpoint save ---
        if time.time() - last_save >= save_interval:
            print(f"  [checkpoint] saving at iter {t:,}...")
            solver.save_checkpoint(checkpoint_path, t, rng.getstate())
            last_save = time.time()

    # --- Final save ---
    total_elapsed = time.time() - run_start
    print(f"\nSaving final checkpoint (iter {t:,})...")
    solver.save_checkpoint(checkpoint_path, t, rng.getstate())

    print(f"Exporting ranges.json...")
    write_ranges_json(solver, t, equity_samples, total_elapsed, output_path)

    print(f"\nDone. Total: {t:,} iterations in {total_elapsed:.0f}s "
          f"({t / total_elapsed:.1f} iter/s)")
    print(f"Run again with the same command to continue from iter {t + 1}.")


def main() -> None:
    parser = argparse.ArgumentParser(description="AOF PLO CFR+ solver (time-based)")
    parser.add_argument("--duration", type=int, default=3600,
                        help="Seconds to run (default: 3600 = 1 hour)")
    parser.add_argument("--equity", type=int, default=500,
                        help="Equity samples per iteration (default: 500)")
    parser.add_argument("--checkpoint", type=str, default=DEFAULT_CHECKPOINT,
                        help="Checkpoint file path")
    parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT,
                        help="Output ranges.json path")
    parser.add_argument("--save-interval", type=int, default=300,
                        help="Seconds between checkpoint saves (default: 300)")
    parser.add_argument("--seed", type=int, default=42,
                        help="RNG seed for fresh runs (ignored when resuming)")
    args = parser.parse_args()

    run_timed(
        duration_seconds=args.duration,
        equity_samples=args.equity,
        checkpoint_path=args.checkpoint,
        output_path=args.output,
        save_interval=args.save_interval,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
