from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class CacheKey:
    provider: str
    season: int
    grand_prix: str
    session_name: str
    resource: str
    driver_code: str | None = None
    lap_number: int | None = None
    schema_version: str = "v1"

    def to_hash(self) -> str:
        payload = {
            "provider": self.provider,
            "season": self.season,
            "grand_prix": self.grand_prix,
            "session_name": self.session_name,
            "resource": self.resource,
            "driver_code": self.driver_code,
            "lap_number": self.lap_number,
            "schema_version": self.schema_version,
        }
        
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()[:20]
    
class CacheManager:
    def __init__(self, cache_root: Path) -> None:
        self.cache_root = cache_root
        self.raw_root = cache_root / "raw"
        self.normalized_root = cache_root / "normalized"
        self.features_root = cache_root / "features"
        
    def initialize(self) -> None:
        self.raw_root.mkdir(parents=True, exist_ok=True)
        self.normalized_root.mkdir(parents=True, exist_ok=True)
        self.features_root.mkdir(parents=True, exist_ok=True)
        
    def build_path(self, key: CacheKey, stage: str = "normalized") -> Path:
        stage_map = {
            "raw": self.raw_root,
            "normalized": self.normalized_root,
            "features": self.features_root,
        }
        
        if stage not in stage_map:
            raise ValueError(f"Invalid cache stage: {stage}")
        
        root = stage_map[stage]
        
        folder = (
            root
            / f"season={key.season}"
            / f"gp={self._slugify(key.grand_prix)}"
            / f"session={self._slugify(key.session_name)}"
            / f"resource={key.resource}"
        )
        
        folder.mkdir(parents=True, exist_ok=True)
        
        file_name = f"{key.to_hash()}.parquet"
        return folder / file_name

    def exists(self, key: CacheKey, stage: str = "normalized") -> bool:
        path = self.build_path(key, stage)
        return path.exists()

    def write_dataframe(
        self,
        df: pd.DataFrame,
        key: CacheKey,
        stage: str = "normalized",
    ) -> Path:
        path = self.build_path(key, stage)
        df.to_parquet(path, index=False)
        return path

    def read_dataframe(
        self,
        key: CacheKey,
        stage: str = "normalized",
    ) -> pd.DataFrame:
        path = self.build_path(key, stage)
        return pd.read_parquet(path)

    @staticmethod
    def _slugify(value: str) -> str:
        return value.strip().lower().replace(" ", "_").replace("/", "_")
