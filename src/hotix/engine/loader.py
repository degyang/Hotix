from pathlib import Path
from typing import Any

import pandas as pd
import yaml

DSL_FILES = [
    "features.yaml",
    "states.yaml",
    "patterns.yaml",
    "transitions.yaml",
    "salience.yaml",
    "pairs.yaml",
    "pair_features.yaml",
    "pair_states.yaml",
    "relation_tags.yaml",
    "regimes.yaml",
    "contexts.yaml",
    "policies.yaml",
]


def load_yaml(path: Path | str) -> dict[str, Any]:
    path = Path(path)
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_registry(path: Path | str) -> dict[str, Any]:
    return load_yaml(path)


def load_all_dsl(dsl_dir: Path | str) -> dict[str, dict[str, Any]]:
    dsl_dir = Path(dsl_dir)
    return {filename[:-5]: load_yaml(dsl_dir / filename) for filename in DSL_FILES}


def load_csv_data(path: Path | str) -> pd.DataFrame:
    path = Path(path)
    df = pd.read_csv(path)
    df = df.rename(
        columns={
            "datetime": "date",
            "vol": "volume",
            "up_count": "adv",
            "down_count": "decl",
        }
    )
    df = df[
        ["date", "open", "high", "low", "close", "volume", "amount", "adv", "decl"]
    ].copy()
    df["date"] = pd.to_datetime(df["date"], format="mixed").dt.strftime("%Y-%m-%d")
    return df.sort_values("date").reset_index(drop=True)


def _resolve_index_csv_path(
    raw_dir: Path, index_id: str, config: dict[str, Any]
) -> Path:
    candidates = []
    symbol = config.get("symbol")
    if symbol:
        candidates.append(raw_dir / f"{symbol}.csv")
    candidates.append(raw_dir / f"{index_id}.csv")

    for path in candidates:
        if path.exists():
            return path

    candidate_names = ", ".join(path.name for path in candidates)
    raise FileNotFoundError(
        f"Missing CSV for index '{index_id}'. Tried: {candidate_names}"
    )


def load_all_data(
    raw_dir: Path | str, registry: dict[str, Any]
) -> dict[str, pd.DataFrame]:
    raw_dir = Path(raw_dir)
    result = {}
    for index_id, config in registry["indices"].items():
        result[index_id] = load_csv_data(
            _resolve_index_csv_path(raw_dir, index_id, config)
        )
    return result
