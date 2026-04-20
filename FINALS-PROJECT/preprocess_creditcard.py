#!/usr/bin/env python3
"""Preprocess a large credit card fraud CSV into lightweight JSON artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple


REQUIRED_COLUMNS = ["Time", "Amount", "Class", "V10", "V12", "V14", "V17"]
AMOUNT_BIN_EDGES = [0, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000]
THRESHOLD_PROFILE_POINTS = 300


@dataclass
class RunningStats:
    count: int = 0
    total: float = 0.0
    min_value: float = float("inf")
    max_value: float = float("-inf")

    def push(self, value: float) -> None:
        self.count += 1
        self.total += value
        self.min_value = min(self.min_value, value)
        self.max_value = max(self.max_value, value)

    def as_dict(self) -> Dict[str, float]:
        if self.count == 0:
            return {"count": 0, "mean": 0.0, "min": 0.0, "max": 0.0}
        return {
            "count": self.count,
            "mean": round(self.total / self.count, 6),
            "min": round(self.min_value, 6),
            "max": round(self.max_value, 6),
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preprocess creditcard.csv for browser visualization")
    parser.add_argument(
        "--input",
        default="data/creditcard.csv",
        help="Input CSV path (default: data/creditcard.csv)",
    )
    parser.add_argument(
        "--output",
        default="processed",
        help="Output directory for JSON files (default: processed)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for deterministic sampling",
    )
    parser.add_argument(
        "--max-legit-points",
        type=int,
        default=10000,
        help="Maximum number of legitimate transactions in scatter sample",
    )
    return parser.parse_args()


def ensure_columns(fieldnames: List[str]) -> None:
    missing = [name for name in REQUIRED_COLUMNS if name not in fieldnames]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")


def safe_float(row: Dict[str, str], key: str) -> float:
    value = row.get(key, "")
    if value is None or value == "":
        return 0.0
    return float(value)


def amount_bucket_index(amount: float) -> int:
    for idx in range(len(AMOUNT_BIN_EDGES) - 1):
        if AMOUNT_BIN_EDGES[idx] <= amount < AMOUNT_BIN_EDGES[idx + 1]:
            return idx
    return len(AMOUNT_BIN_EDGES) - 1


def amount_bucket_labels() -> List[str]:
    labels: List[str] = []
    for idx in range(len(AMOUNT_BIN_EDGES) - 1):
        labels.append(f"{AMOUNT_BIN_EDGES[idx]}-{AMOUNT_BIN_EDGES[idx + 1]}")
    labels.append(f">={AMOUNT_BIN_EDGES[-1]}")
    return labels


def fraud_score(row: Dict[str, str], amount: float) -> float:
    v14 = abs(safe_float(row, "V14"))
    v17 = abs(safe_float(row, "V17"))
    v12 = abs(safe_float(row, "V12"))
    v10 = abs(safe_float(row, "V10"))
    amount_term = math.log1p(max(amount, 0.0))
    return (0.42 * v14) + (0.24 * v17) + (0.16 * v12) + (0.10 * v10) + (0.08 * amount_term)


def correlation(points: List[Tuple[float, float]]) -> float:
    if not points:
        return 0.0
    n = len(points)
    sx = sum(p[0] for p in points)
    sy = sum(p[1] for p in points)
    mx = sx / n
    my = sy / n
    cov = sum((p[0] - mx) * (p[1] - my) for p in points)
    var_x = sum((p[0] - mx) ** 2 for p in points)
    var_y = sum((p[1] - my) ** 2 for p in points)
    if var_x == 0 or var_y == 0:
        return 0.0
    return cov / math.sqrt(var_x * var_y)


def metric_snapshot(tp: int, fp: int, total_pos: int, total_neg: int) -> Dict[str, float]:
    fn = total_pos - tp
    tn = total_neg - fp

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / total_pos if total_pos else 0.0
    specificity = tn / total_neg if total_neg else 0.0
    fpr = fp / total_neg if total_neg else 0.0
    accuracy = (tp + tn) / (total_pos + total_neg) if (total_pos + total_neg) else 0.0
    f1 = 0.0 if (precision + recall) == 0 else (2 * precision * recall) / (precision + recall)

    return {
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "specificity": specificity,
        "fpr": fpr,
        "accuracy": accuracy,
        "f1": f1,
    }


def compute_metrics(scored_rows: List[Tuple[float, int]], total_pos: int, total_neg: int) -> Dict[str, object]:
    if total_pos == 0:
        raise ValueError("No positive class rows found; cannot compute precision-recall metrics")

    ranked = sorted(scored_rows, key=lambda x: x[0], reverse=True)
    baseline_positive_rate = total_pos / (total_pos + total_neg)

    tp = 0
    fp = 0
    prev_recall = 0.0
    average_precision = 0.0
    best_f1 = -1.0
    best_threshold = ranked[0][0]
    best_snapshot = metric_snapshot(0, 0, total_pos, total_neg)
    best_rank_index = 0

    curve_points: List[Dict[str, float]] = []
    interval = max(1, len(ranked) // 600)
    threshold_interval = max(1, len(ranked) // THRESHOLD_PROFILE_POINTS)
    threshold_points: List[Dict[str, float]] = []

    for idx, (score, label) in enumerate(ranked, start=1):
        if label == 1:
            tp += 1
        else:
            fp += 1

        snapshot = metric_snapshot(tp, fp, total_pos, total_neg)
        precision = snapshot["precision"]
        recall = snapshot["recall"]

        if recall > prev_recall:
            average_precision += (recall - prev_recall) * precision
            prev_recall = recall

        f1 = snapshot["f1"]
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = score
            best_snapshot = snapshot
            best_rank_index = idx

        if idx % interval == 0 or label == 1 or idx == len(ranked):
            curve_points.append(
                {
                    "precision": round(precision, 6),
                    "recall": round(recall, 6),
                }
            )

        if idx == 1 or idx % threshold_interval == 0 or idx == len(ranked):
            threshold_points.append(
                {
                    "rank_index": idx,
                    "threshold": round(score, 6),
                    "tp": int(snapshot["tp"]),
                    "fp": int(snapshot["fp"]),
                    "tn": int(snapshot["tn"]),
                    "fn": int(snapshot["fn"]),
                    "precision": round(snapshot["precision"], 6),
                    "recall": round(snapshot["recall"], 6),
                    "specificity": round(snapshot["specificity"], 6),
                    "fpr": round(snapshot["fpr"], 6),
                    "accuracy": round(snapshot["accuracy"], 6),
                    "f1": round(snapshot["f1"], 6),
                }
            )

    best_point = {
        "rank_index": best_rank_index,
        "threshold": round(best_threshold, 6),
        "tp": int(best_snapshot["tp"]),
        "fp": int(best_snapshot["fp"]),
        "tn": int(best_snapshot["tn"]),
        "fn": int(best_snapshot["fn"]),
        "precision": round(best_snapshot["precision"], 6),
        "recall": round(best_snapshot["recall"], 6),
        "specificity": round(best_snapshot["specificity"], 6),
        "fpr": round(best_snapshot["fpr"], 6),
        "accuracy": round(best_snapshot["accuracy"], 6),
        "f1": round(best_snapshot["f1"], 6),
    }

    threshold_by_rank: Dict[int, Dict[str, float]] = {
        int(point["rank_index"]): point for point in threshold_points
    }
    threshold_by_rank[best_rank_index] = best_point
    threshold_profile_points = [threshold_by_rank[k] for k in sorted(threshold_by_rank.keys())]

    recommended_index = 0
    for idx, point in enumerate(threshold_profile_points):
        if int(point["rank_index"]) == best_rank_index:
            recommended_index = idx
            break

    deciles: List[Dict[str, object]] = []
    cumulative_fraud = 0
    total_ranked = len(ranked)

    for decile_idx in range(10):
        start = (decile_idx * total_ranked) // 10
        end = ((decile_idx + 1) * total_ranked) // 10
        segment = ranked[start:end]
        segment_total = len(segment)
        segment_fraud = sum(label for _, label in segment)

        cumulative_fraud += segment_fraud

        segment_rate = (segment_fraud / segment_total) if segment_total else 0.0
        cumulative_capture = cumulative_fraud / total_pos

        deciles.append(
            {
                "decile": decile_idx + 1,
                "start_rank": start + 1 if segment_total else 0,
                "end_rank": end,
                "total": segment_total,
                "fraud_count": segment_fraud,
                "fraud_rate": round(segment_rate, 6),
                "cumulative_fraud_captured": round(cumulative_capture, 6),
                "lift_vs_baseline": round((segment_rate / baseline_positive_rate) if baseline_positive_rate else 0.0, 6),
            }
        )

    tp_best = int(best_snapshot["tp"])
    fp_best = int(best_snapshot["fp"])
    tn_best = int(best_snapshot["tn"])
    fn_best = int(best_snapshot["fn"])

    return {
        "scoring_note": "Heuristic score from V14, V17, V12, V10, and Amount. This is not a trained model.",
        "auprc": round(average_precision, 6),
        "baseline_positive_rate": round(baseline_positive_rate, 6),
        "best_f1_threshold": round(best_threshold, 6),
        "best_f1": round(best_f1, 6),
        "confusion_matrix": {
            "tp": tp_best,
            "fp": fp_best,
            "tn": tn_best,
            "fn": fn_best,
        },
        "rates": {
            "precision": round(best_snapshot["precision"], 6),
            "recall": round(best_snapshot["recall"], 6),
            "specificity": round(best_snapshot["specificity"], 6),
            "fpr": round(best_snapshot["fpr"], 6),
            "accuracy": round(best_snapshot["accuracy"], 6),
        },
        "pr_curve": curve_points,
        "lift": {
            "baseline_positive_rate": round(baseline_positive_rate, 6),
            "deciles": deciles,
        },
        "threshold_profile": {
            "sampling_interval": threshold_interval,
            "recommended_index": recommended_index,
            "points": threshold_profile_points,
        },
    }


def main() -> None:
    args = parse_args()
    script_dir = Path(__file__).resolve().parent
    input_path = (script_dir / args.input).resolve() if not Path(args.input).is_absolute() else Path(args.input)
    output_dir = (script_dir / args.output).resolve() if not Path(args.output).is_absolute() else Path(args.output)

    output_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed)

    amount_labels = amount_bucket_labels()
    amount_legit = [0] * len(amount_labels)
    amount_fraud = [0] * len(amount_labels)

    hourly_legit = [0] * 24
    hourly_fraud = [0] * 24

    scored_rows: List[Tuple[float, int]] = []
    legit_sample: List[Dict[str, float]] = []
    fraud_sample: List[Dict[str, float]] = []
    legit_seen = 0

    feature_names = [f"V{i}" for i in range(1, 29)]
    feature_sum_legit = {name: 0.0 for name in feature_names}
    feature_sum_fraud = {name: 0.0 for name in feature_names}

    amount_stats_overall = RunningStats()
    amount_stats_legit = RunningStats()
    amount_stats_fraud = RunningStats()

    amount_vs_score_points: List[Tuple[float, float]] = []

    total_rows = 0
    fraud_rows = 0

    with input_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("Input CSV has no header")
        ensure_columns(reader.fieldnames)

        for row in reader:
            total_rows += 1

            cls = int(float(row["Class"]))
            time_seconds = safe_float(row, "Time")
            amount = safe_float(row, "Amount")
            time_hour = (time_seconds % 86400.0) / 3600.0

            score = fraud_score(row, amount)
            scored_rows.append((score, cls))
            amount_vs_score_points.append((math.log1p(max(amount, 0.0)), score))

            amount_stats_overall.push(amount)
            bucket = amount_bucket_index(amount)
            hour_idx = max(0, min(23, int(time_hour)))

            point_payload = {
                "time_hour": round(time_hour, 4),
                "amount": round(amount, 6),
                "amount_log10": round(math.log10(max(amount, 0.0) + 1.0), 6),
                "score_hint": round(score, 6),
                "class": cls,
            }

            if cls == 1:
                fraud_rows += 1
                amount_stats_fraud.push(amount)
                amount_fraud[bucket] += 1
                hourly_fraud[hour_idx] += 1
                fraud_sample.append(point_payload)
                for name in feature_names:
                    feature_sum_fraud[name] += safe_float(row, name)
            else:
                amount_stats_legit.push(amount)
                amount_legit[bucket] += 1
                hourly_legit[hour_idx] += 1
                for name in feature_names:
                    feature_sum_legit[name] += safe_float(row, name)

                legit_seen += 1
                if len(legit_sample) < args.max_legit_points:
                    legit_sample.append(point_payload)
                else:
                    replace_idx = rng.randint(0, legit_seen - 1)
                    if replace_idx < args.max_legit_points:
                        legit_sample[replace_idx] = point_payload

    legit_rows = total_rows - fraud_rows
    metrics = compute_metrics(scored_rows, fraud_rows, legit_rows)

    feature_gap: List[Dict[str, float]] = []
    for name in feature_names:
        legit_mean = feature_sum_legit[name] / legit_rows if legit_rows else 0.0
        fraud_mean = feature_sum_fraud[name] / fraud_rows if fraud_rows else 0.0
        feature_gap.append(
            {
                "feature": name,
                "legit_mean": round(legit_mean, 6),
                "fraud_mean": round(fraud_mean, 6),
                "abs_gap": round(abs(fraud_mean - legit_mean), 6),
            }
        )
    feature_gap.sort(key=lambda x: x["abs_gap"], reverse=True)

    overview = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_transactions": total_rows,
        "fraud_transactions": fraud_rows,
        "legit_transactions": legit_rows,
        "fraud_rate": round((fraud_rows / total_rows) if total_rows else 0.0, 6),
        "fraud_rate_pct": round(((fraud_rows / total_rows) * 100.0) if total_rows else 0.0, 4),
        "amount_stats": {
            "overall": amount_stats_overall.as_dict(),
            "legit": amount_stats_legit.as_dict(),
            "fraud": amount_stats_fraud.as_dict(),
        },
        "amount_score_correlation": round(correlation(amount_vs_score_points), 6),
    }

    distributions = {
        "amount_bins": [
            {
                "label": amount_labels[idx],
                "legit_count": amount_legit[idx],
                "fraud_count": amount_fraud[idx],
            }
            for idx in range(len(amount_labels))
        ],
        "hourly": [
            {
                "hour": idx,
                "legit_count": hourly_legit[idx],
                "fraud_count": hourly_fraud[idx],
            }
            for idx in range(24)
        ],
        "feature_gap_all": feature_gap,
        "feature_gap_top10": feature_gap[:10],
    }

    sampled_points = {
        "metadata": {
            "sampling": "all fraud rows + deterministic reservoir sample of legitimate rows",
            "seed": args.seed,
            "legit_sample_limit": args.max_legit_points,
            "legit_sample_size": len(legit_sample),
            "fraud_sample_size": len(fraud_sample),
        },
        "points": fraud_sample + legit_sample,
    }

    artifacts = {
        "overview.json": overview,
        "distributions.json": distributions,
        "sample_points.json": sampled_points,
        "metrics.json": metrics,
    }

    for filename, payload in artifacts.items():
        output_path = output_dir / filename
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, separators=(",", ":"), ensure_ascii=True)

    print("Preprocessing complete")
    print(f"Input: {input_path}")
    print(f"Output directory: {output_dir}")
    print(f"Rows: {total_rows}")
    print(f"Fraud rows: {fraud_rows}")
    print(f"Legit rows: {legit_rows}")
    print(f"Fraud rate: {overview['fraud_rate_pct']}%")
    print(f"AUPRC (heuristic): {metrics['auprc']}")


if __name__ == "__main__":
    main()
