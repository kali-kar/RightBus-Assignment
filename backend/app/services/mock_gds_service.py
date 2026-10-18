import json
from app.core.config import DATASET_PATH


class DatasetError(Exception):
    pass


def load_dataset() -> dict:
    """Read the supplied JSON from disk on each call (small file; keeps tests/data edits honest)."""
    try:
        with open(DATASET_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        raise DatasetError(f"Cannot load dataset: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("trips"), list):
        raise DatasetError("Dataset has no 'trips' list")
    return data
