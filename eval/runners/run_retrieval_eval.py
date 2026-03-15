from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import subprocess
from typing import Any, Dict, List, Optional

from backend.app.core.config import settings
from backend.app.schemas.recipe import RecipeFilters
from backend.app.services.rag_service import RagService
from eval.metrics.retrieval_metrics import evaluate_case


def _load_dataset(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _build_filters(raw: Optional[Dict[str, Any]]) -> Optional[RecipeFilters]:
    if raw is None:
        return None
    return RecipeFilters.model_validate(raw)


def _mean(values: List[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / float(len(values))


def _git_commit() -> Optional[str]:
    try:
        output = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
        return output.decode("utf-8").strip()
    except Exception:
        return None


def _write_csv(path: str, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _run_strategy(
    rag: RagService,
    case: Dict[str, Any],
    strategy_name: str,
    use_filters: bool,
    rerank: bool,
) -> Dict[str, Any]:
    filters = _build_filters(case.get("filters")) if use_filters else None
    metrics_filters = _build_filters(case.get("filters"))
    results, diagnostics = rag.search_with_diagnostics(
        query=case["query"],
        top_k=case.get("top_k", 5),
        filters=filters,
        rerank=rerank,
        candidate_k=case.get("candidate_k"),
        include_diagnostics=True,
    )

    metrics = evaluate_case(
        rag=rag,
        results=results,
        expected_ids=case.get("expected_relevant_ids", []),
        excluded_ids=case.get("excluded_ids", []),
        filters=metrics_filters,
    )

    retrieved_ids = [r.get("id") for r in results]
    retrieved_scores = [r.get("score") for r in results]
    expect_empty = bool(case.get("expect_empty", False))
    empty_ok = (len(results) == 0) == expect_empty

    return {
        "case_id": case.get("id"),
        "strategy": strategy_name,
        "query": case.get("query"),
        "top_k": case.get("top_k", 5),
        "filters": case.get("filters"),
        "expected_relevant_ids": case.get("expected_relevant_ids", []),
        "excluded_ids": case.get("excluded_ids", []),
        "expect_empty": expect_empty,
        "empty_ok": empty_ok,
        "retrieved_ids": retrieved_ids,
        "retrieved_scores": retrieved_scores,
        "diagnostics": diagnostics.model_dump() if diagnostics else None,
        **metrics,
    }


def run(args: argparse.Namespace) -> None:
    dataset = _load_dataset(args.dataset)
    cases = dataset.get("cases", [])
    if not os.path.exists(settings.FAISS_INDEX_PATH) or not os.path.exists(settings.RECIPES_PKL_PATH):
        raise RuntimeError(
            "RAG artifacts not found. Build them with: "
            "python scripts/build_rag_index.py --recipes data/sample_recipes.json --out-dir models/"
        )
    rag = RagService(settings.FAISS_INDEX_PATH, settings.RECIPES_PKL_PATH)

    strategies = [
        ("baseline", False, False),
        ("filtered", True, False),
        ("reranked", True, True),
    ]

    results: List[Dict[str, Any]] = []
    for case in cases:
        for strategy_name, use_filters, rerank in strategies:
            results.append(_run_strategy(rag, case, strategy_name, use_filters, rerank))

    summary: Dict[str, Any] = {}
    for strategy_name, _, _ in strategies:
        strategy_rows = [row for row in results if row["strategy"] == strategy_name]
        hit_rates = [row["hit_at_k"] for row in strategy_rows]
        recalls = [row["recall_at_k"] for row in strategy_rows if row["recall_at_k"] is not None]
        summary[strategy_name] = {
            "cases": len(strategy_rows),
            "hit_rate": _mean(hit_rates),
            "recall_avg": _mean(recalls),
            "filter_violations": sum(row["filter_violations"] for row in strategy_rows),
            "excluded_violations": sum(row["excluded_violations"] for row in strategy_rows),
            "empty_correct": sum(1 for row in strategy_rows if row["empty_ok"]),
        }

    os.makedirs(args.out_dir, exist_ok=True)
    run_id = args.run_id or dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d_%H%M%S")

    payload = {
        "run_id": run_id,
        "dataset_path": args.dataset,
        "dataset_version": dataset.get("version"),
        "faiss_index_path": settings.FAISS_INDEX_PATH,
        "recipes_pkl_path": settings.RECIPES_PKL_PATH,
        "git_commit": _git_commit(),
        "strategies": [name for name, _, _ in strategies],
        "summary": summary,
        "cases": results,
    }

    json_path = os.path.join(args.out_dir, f"retrieval_eval_{run_id}.json")
    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)

    csv_path = os.path.join(args.out_dir, f"retrieval_eval_{run_id}.csv")
    csv_fields = [
        "case_id",
        "strategy",
        "query",
        "top_k",
        "hit_at_k",
        "recall_at_k",
        "filter_violations",
        "excluded_violations",
        "expect_empty",
        "empty_ok",
        "retrieved_ids",
        "retrieved_scores",
    ]
    csv_rows = [
        {field: row.get(field) for field in csv_fields}
        for row in results
    ]
    _write_csv(csv_path, csv_rows, csv_fields)

    print("Retrieval evaluation complete.")
    print(f"Run ID: {run_id}")
    print(f"JSON: {json_path}")
    print(f"CSV:  {csv_path}")
    print("Summary:")
    for strategy_name, metrics in summary.items():
        print(f"- {strategy_name}: hit_rate={metrics['hit_rate']:.2f}, recall_avg={metrics['recall_avg']:.2f}, "
              f"filter_violations={metrics['filter_violations']}, excluded_violations={metrics['excluded_violations']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run retrieval evaluation for NourishAI.")
    parser.add_argument(
        "--dataset",
        default="eval/datasets/retrieval_eval.json",
        help="Path to retrieval evaluation dataset JSON.",
    )
    parser.add_argument(
        "--out-dir",
        default="eval/outputs",
        help="Directory to write evaluation artifacts.",
    )
    parser.add_argument("--run-id", default=None, help="Optional run identifier.")
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
