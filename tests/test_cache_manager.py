from pathlib import Path

import pandas as pd

from data.cache.cache_manager import CacheKey, CacheManager


def test_cache_manager_write_and_read(tmp_path: Path) -> None:
    cache_manager = CacheManager(tmp_path / "cache")
    cache_manager.initialize()

    key = CacheKey(
        provider="test_provider",
        season=2024,
        grand_prix="Italy",
        session_name="Race",
        resource="laps",
    )

    df_original = pd.DataFrame(
        {
            "driver": ["VER", "LEC"],
            "lap_time": [80.1, 80.5],
        }
    )

    cache_manager.write_dataframe(df_original, key)
    df_loaded = cache_manager.read_dataframe(key)

    assert not df_loaded.empty
    assert list(df_loaded.columns) == ["driver", "lap_time"]