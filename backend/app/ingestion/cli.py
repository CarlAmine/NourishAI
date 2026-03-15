from __future__ import annotations

import argparse
import json

from .pipeline import run_ingestion
from ..core.config import settings


def main() -> None:
    parser = argparse.ArgumentParser(description="NourishAI ingestion pipeline")
    parser.add_argument("--data-dir", default=settings.DATA_DIR, help="Data directory containing recipes/nutrition/ingredients")
    parser.add_argument("--recreate", action="store_true", help="Drop and recreate the vector collection")
    parser.add_argument("--batch-size", type=int, default=64, help="Embedding batch size")
    args = parser.parse_args()

    report = run_ingestion(data_dir=args.data_dir, recreate=args.recreate, batch_size=args.batch_size)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
