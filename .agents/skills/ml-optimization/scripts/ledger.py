#!/usr/bin/env python3
"""Deterministic experiment ledger, paired bootstrap statistics, and RUNS.md generator.

Zero external dependencies (Python 3.9+ stdlib only).
Part of the `ml-optimization` Agent Skill.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha256_file(path: str | None) -> str | None:
    if not path:
        return None
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"File not found for hashing: {path}")
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:12]


def load_scores(path: str) -> list[float]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [float(x) for x in data]
    if isinstance(data, dict):
        if "scores" in data and isinstance(data["scores"], list):
            return [float(x) for x in data["scores"]]
        return [float(data[k]) for k in sorted(data.keys())]
    raise ValueError(f"Unsupported score JSON format in {path}: expected list or dict")


def load_ledger(ledger_path: Path) -> list[dict[str, Any]]:
    if not ledger_path.exists():
        return []
    records: list[dict[str, Any]] = []
    for idx, line in enumerate(ledger_path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on line {idx} of {ledger_path}: {exc}") from exc
    return records


def cmd_init(args: argparse.Namespace) -> int:
    root = Path(args.dir).resolve()
    for sub in ("work/harness", "work/variants", "work/logs", "work/artifacts"):
        (root / sub).mkdir(parents=True, exist_ok=True)

    ledger = root / "LEDGER.jsonl"
    if not ledger.exists():
        ledger.write_text("", encoding="utf-8")

    scaffolds = {
        "BRIEF.md": (
            "# Brief\n"
            "- **Objective (1 sentence, direction, units):**\n"
            "- **Metric command:** `<cmd>` | **Baseline:** `<val>`\n"
            "- **Hard constraints:**\n"
            "- **Allowed / Forbidden (data & legitimacy policy):**\n"
            "- **Budget & Kill criteria:**\n"
            "- **Definition of Done:**\n"
        ),
        "METRIC.md": (
            "# Metric Decomposition\n"
            "- **Formula / code path:**\n"
            "- **Direction:** maximize | minimize\n"
            "- **Theoretical ceiling:** | **Practical optimum:**\n\n"
            "| Term | Weight | Max | Floor | Headroom | Status |\n"
            "|---|---|---|---|---|---|\n"
        ),
        "IDEAS.md": (
            "# Structural Idea Backlog\n\n"
            "| ID | Hypothesis / Mechanism | Est. Gain | Conf | Cost | Cheapest Probe | Status |\n"
            "|---|---|---|---|---|---|---|\n"
        ),
    }
    created = []
    for fname, content in scaffolds.items():
        target = root / fname
        if not target.exists():
            target.write_text(content, encoding="utf-8")
            created.append(fname)

    print(f"Initialized ML optimization workspace at {root} (created: {', '.join(created) or 'dirs only'})")
    return 0


def cmd_log(args: argparse.Namespace) -> int:
    ledger_path = Path(args.ledger)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    records = load_ledger(ledger_path)

    exp_id = args.id or f"E-{len(records) + 1:04d}"
    record: dict[str, Any] = {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "id": exp_id,
        "phase": args.phase,
        "name": args.name,
        "base_hash": sha256_file(args.base),
        "variant_hash": sha256_file(args.variant),
        "overrides": json.loads(args.overrides),
        "dataset": args.dataset,
        "command": args.command,
        "metrics": json.loads(args.metrics),
        "cost": json.loads(args.cost),
        "verdict": args.verdict,
        "notes": args.notes,
    }

    with ledger_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")

    print(f"Logged {exp_id} [{args.phase}] {args.name} verdict={args.verdict} metrics={record['metrics']}")
    return 0


def paired_bootstrap_ci(
    deltas: list[float], n_boot: int, seed: int
) -> tuple[float, float]:
    n = len(deltas)
    if n == 0:
        return (0.0, 0.0)
    if n == 1:
        return (deltas[0], deltas[0])
    rng = random.Random(seed)
    means: list[float] = []
    for _ in range(n_boot):
        total = 0.0
        for _ in range(n):
            total += deltas[rng.randrange(n)]
        means.append(total / n)
    means.sort()
    lo_idx = max(0, int(0.025 * n_boot))
    hi_idx = min(n_boot - 1, int(0.975 * n_boot))
    return (means[lo_idx], means[hi_idx])


def cmd_compare(args: argparse.Namespace) -> int:
    if args.noise_floor:
        run_means = [statistics.fmean(load_scores(p)) for p in args.noise_floor]
        if len(run_means) < 2:
            raise ValueError("--noise-floor requires at least 2 baseline score files")
        mean_val = statistics.fmean(run_means)
        std_val = statistics.stdev(run_means)
        result = {
            "runs": len(run_means),
            "mean": round(mean_val, 8),
            "std_of_mean": round(std_val, 8),
            "mde_2sigma": round(2.0 * std_val, 8),
        }
        print(json.dumps(result, indent=2))
        return 0

    if not args.baseline or not args.candidate:
        raise ValueError("Provide --baseline and --candidate (or --noise-floor)")

    base = load_scores(args.baseline)
    cand = load_scores(args.candidate)
    if len(base) != len(cand):
        raise ValueError(f"Unpaired lengths: baseline={len(base)} vs candidate={len(cand)}")
    if not base:
        raise ValueError("Score arrays are empty")

    sign = 1.0 if args.direction == "maximize" else -1.0
    # Positive `gain` always means improvement in the desired direction.
    gains = [sign * (c - b) for b, c in zip(base, cand)]
    mean_base = statistics.fmean(base)
    mean_cand = statistics.fmean(cand)
    mean_gain = statistics.fmean(gains)
    median_gain = statistics.median(gains)
    ci_lo, ci_hi = paired_bootstrap_ci(gains, args.n_boot, args.seed)

    # Worst-K tail check (bottom 5% or at least 1 example in direction of worse score).
    k = max(1, math.ceil(0.05 * len(base)))
    worst_base = sorted(sign * x for x in base)[:k]
    worst_cand = sorted(sign * x for x in cand)[:k]
    tail_gain = statistics.fmean(worst_cand) - statistics.fmean(worst_base)

    threshold = max(args.mde, args.min_effect)
    if args.constraint_regression:
        verdict = "reject"
        reason = "hard constraint regression"
    elif mean_gain > threshold and ci_lo > 0.0:
        verdict = "keep"
        reason = f"paired gain {mean_gain:.6g} > threshold {threshold:.6g} and 95% CI > 0"
    elif mean_gain <= 0.0 or ci_hi <= 0.0:
        verdict = "reject"
        reason = f"no positive improvement (gain={mean_gain:.6g}, ci95=[{ci_lo:.6g}, {ci_hi:.6g}])"
    else:
        verdict = "inconclusive"
        reason = f"gain {mean_gain:.6g} within noise/threshold ({threshold:.6g}) or CI crosses 0"

    out = {
        "n": len(base),
        "direction": args.direction,
        "baseline_mean": round(mean_base, 8),
        "candidate_mean": round(mean_cand, 8),
        "paired_gain_mean": round(mean_gain, 8),
        "paired_gain_median": round(median_gain, 8),
        "ci95_gain": [round(ci_lo, 8), round(ci_hi, 8)],
        "worst_5pct_tail_gain": round(tail_gain, 8),
        "improved_fraction": round(sum(1 for g in gains if g > 0) / len(gains), 4),
        "threshold": threshold,
        "verdict": verdict,
        "reason": reason,
    }
    print(json.dumps(out, indent=2))
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    ledger_path = Path(args.ledger)
    records = load_ledger(ledger_path)
    if not records:
        print("Ledger is empty.")
        return 0

    metric = args.metric
    reverse = args.direction == "maximize"

    def metric_val(rec: dict[str, Any]) -> float:
        v = rec.get("metrics", {}).get(metric)
        if v is None:
            return float("-inf") if reverse else float("inf")
        return float(v)

    base_rec = next((r for r in records if r.get("id") == args.baseline_id), records[0])
    base_val = base_rec.get("metrics", {}).get(metric)

    ordered = sorted(records, key=metric_val, reverse=reverse)

    lines = [
        f"# Experiment Runs (`{metric}`, {args.direction})",
        "",
        f"> Auto-generated from `{ledger_path.name}` ({len(records)} runs). Baseline: `{base_rec['id']}` = `{base_val}`.",
        "",
        f"| ID | Phase | Name | {metric} | Delta vs {base_rec['id']} | Dataset | Verdict | Notes |",
        "|---|---|---|---:|---:|---|---|---|",
    ]
    for r in ordered:
        v = r.get("metrics", {}).get(metric)
        if v is not None and base_val is not None:
            delta_str = f"{float(v) - float(base_val):+.6g}"
        else:
            delta_str = "—"
        v_str = f"{float(v):.6g}" if v is not None else "—"
        notes = str(r.get("notes", "")).replace("|", "/")[:60]
        lines.append(
            f"| {r['id']} | {r.get('phase', '')} | {r.get('name', '')} | {v_str} | {delta_str} "
            f"| {r.get('dataset', '')} | {r.get('verdict', '')} | {notes} |"
        )

    content = "\n".join(lines) + "\n"
    out_path = Path(args.output)
    out_path.write_text(content, encoding="utf-8")

    # Print compact stdout digest (top 10 rows only to keep output <= 2 KB).
    preview = "\n".join(lines[: min(len(lines), 16)])
    print(f"Wrote {out_path} ({len(records)} runs).\n{preview}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Deterministic ML experiment ledger & paired stats CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Initialize workspace directories and ledger files")
    p_init.add_argument("dir", nargs="?", default=".", help="Project workspace directory")
    p_init.set_defaults(func=cmd_init)

    p_log = sub.add_parser("log", help="Append a validated record to LEDGER.jsonl")
    p_log.add_argument("--ledger", default="LEDGER.jsonl")
    p_log.add_argument("--id", default=None)
    p_log.add_argument("--phase", required=True, choices=["baseline", "param", "structure", "verify"])
    p_log.add_argument("--name", required=True)
    p_log.add_argument("--metrics", required=True, help='JSON dict, e.g. \'{"score": 0.91}\'')
    p_log.add_argument("--verdict", required=True, choices=["keep", "reject", "inconclusive", "baseline"])
    p_log.add_argument("--dataset", default="dev")
    p_log.add_argument("--command", default="")
    p_log.add_argument("--overrides", default="{}")
    p_log.add_argument("--cost", default="{}")
    p_log.add_argument("--base", default=None, help="Path to canonical base file (hashed)")
    p_log.add_argument("--variant", default=None, help="Path to variant file (hashed)")
    p_log.add_argument("--notes", default="")
    p_log.set_defaults(func=cmd_log)

    p_cmp = sub.add_parser("compare", help="Paired bootstrap comparison or baseline noise-floor MDE")
    p_cmp.add_argument("--baseline", help="JSON file of per-example baseline scores")
    p_cmp.add_argument("--candidate", help="JSON file of per-example candidate scores")
    p_cmp.add_argument("--noise-floor", nargs="+", help="k>=2 baseline score files to estimate MDE")
    p_cmp.add_argument("--direction", default="maximize", choices=["maximize", "minimize"])
    p_cmp.add_argument("--mde", type=float, default=0.0)
    p_cmp.add_argument("--min-effect", type=float, default=0.0)
    p_cmp.add_argument("--constraint-regression", action="store_true")
    p_cmp.add_argument("--n-boot", type=int, default=2000)
    p_cmp.add_argument("--seed", type=int, default=0)
    p_cmp.set_defaults(func=cmd_compare)

    p_sum = sub.add_parser("summary", help="Generate RUNS.md sorted leaderboard from LEDGER.jsonl")
    p_sum.add_argument("--ledger", default="LEDGER.jsonl")
    p_sum.add_argument("--output", default="RUNS.md")
    p_sum.add_argument("--metric", required=True)
    p_sum.add_argument("--direction", default="maximize", choices=["maximize", "minimize"])
    p_sum.add_argument("--baseline-id", default=None)
    p_sum.set_defaults(func=cmd_summary)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
