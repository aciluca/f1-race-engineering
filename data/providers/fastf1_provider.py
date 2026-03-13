from __future__ import annotations

from pathlib import Path
from typing import Any

import fastf1
import pandas as pd

from data.providers.base import BaseSessionProvider


class FastF1Provider(BaseSessionProvider):
    def __init__(self, cache_dir: Path) -> None:
        self.cache_dir = cache_dir
        fastf1.Cache.enable_cache(str(cache_dir))
        
    def provider_name(self) -> str:
        return "fastf1"
    
    def _load_session(self, season: int, grand_prix: str, session_name: str):
        session = fastf1.get_session(season, grand_prix, session_name)
        session.load()
        return session
    
    def get_session_metadata(
        self,
        season: int,
        grand_prix: str,
        session_name: str,
    ) -> dict[str, Any]:
        session = self._load_session(season, grand_prix, session_name)
        
        return {
            "event_name": session.event["EventName"],
            "session_name": session.name,
            "date": str(session.date),
        }
    
    def get_laps(
        self,
        season: int,
        grand_prix: str,
        session_name: str,
    ) -> pd.DataFrame:
        session = self._load_session(season, grand_prix, session_name)
        return pd.DataFrame(session.laps)
    
    def get_telemetry(
        self,
        season: int,
        grand_prix: str,
        session_name: str,
        driver_code: str,
        lap_number: int | None = None,
    ) -> pd.DataFrame:
        session = self._load_session(season, grand_prix, session_name)
        
        laps = session.laps.pick_drivers(driver_code)
        
        if lap_number is not None:
            laps = laps[laps["LapNumber"] == lap_number]
            
        if laps.empty:
            return pd.DataFrame()
        
        lap = laps.iloc[0]
        telemetry = lap.get_car_data().add_distance()
        
        return pd.DataFrame(telemetry)
    
    def get_weather(
        self,
        season: int,
        grand_prix: str,
        session_name: str,
    ) -> pd.DataFrame:
        session = self._load_session(season, grand_prix, session_name)
        return pd.DataFrame(session.weather_data)
