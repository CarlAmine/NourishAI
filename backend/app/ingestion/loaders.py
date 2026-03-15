from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger("nourishai.ingestion")


def load_recipe_records(data_dir: str) -> List[Dict[str, Any]]:
    return _load_records(Path(data_dir) / "recipes", "recipes")


def load_nutrition_records(data_dir: str) -> List[Dict[str, Any]]:
    return _load_records(Path(data_dir) / "nutrition", "nutrition")


def load_ingredient_records(data_dir: str) -> List[Dict[str, Any]]:
    return _load_records(Path(data_dir) / "ingredients", "ingredients")


def _load_records(folder: Path, label: str) -> List[Dict[str, Any]]:
    if not folder.exists():
        logger.warning("%s data folder not found: %s", label, folder)
        return []

    records: List[Dict[str, Any]] = []
    for path in sorted(folder.glob("*.json")):
        try:
            with path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except Exception as exc:
            logger.warning("Failed to load %s: %s", path, exc)
            continue

        if isinstance(payload, list):
            records.extend(payload)
        elif isinstance(payload, dict):
            if isinstance(payload.get("items"), list):
                records.extend(payload["items"])
            else:
                records.append(payload)
        else:
            logger.warning("Unsupported payload format in %s", path)

    logger.info("Loaded %d %s records", len(records), label)
    return records
