from __future__ import annotations

from typing import Any

import pandas as pd
import requests

from data.provides.base import BaseSessionProvider

class OpenF1Provider(BaseSessionProvider):
    BASE_URL = "https://api.openf1.org/v1"
    
    def provider_name(self) -> str:
        return "openf1"
    
    def get_event_schedule(self, season: int) -> pd.DataFrame:
        response = requests.get(
            f"{self.BASE_URL}/meetings",
            params={"year": season},
            timeout=30,  
        )
        response.raise_for_status()
        return pd.DataFrame(response.json())
    
    def get_session_metadata(
        self,
        season: int,
        grand_prix: str,
        session_name: str,
    ) -> dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/sessions",
            params={
                "year": season,
                "country_name": grand_prix,
                "session_name": session_name,
            },
            timeout=30,
        )
        response.raise_for_status()
        
        sessions = response.json()
        if not sessions:
            return {}
        
        return sessions[0]
    
    def get_laps(
        self,
        season: int,
        grand_prix: str,
        session_name: str,
    ) -> pd.DataFrame:
        session = self.get_session_metadata(season, grand_prix, session_name)
        if not session:
            return pd.DataFrame()
        
        response = requests.get(
            f"{self.BASE_URL}/laps",
            params={"session_key": session["session_key"]},
            timeout=60,
        )
        response.raise_for_status()
        
        return pd.DataFrame(response.json)
    
    def get_telemetry(
        self,
        season: int,
        grand_prix: str,
        session_name: str,
        driver_code: str,
        lap_number: int | None = None,
    ) -> pd.DataFrame:
        session = self.get_session_metadata(season, grand_prix, session_name)
        if not session:
            return pd.DataFrame()

        params = {
            "session_key": session["session_key"],
            "driver_number": driver_code,
        }
        
        response = requests.get(
            f"{self.BASE_URL}/car_data",
            params=params,
            timeout=60,
        )
        response.raise_for_status()
        
        df = pd.DataFrame(response.json())
        
        if lap_number is not None and "lap_number" in df.columns:
            df = df[df["lap_number"] == lap_number]
            
        return df
    
    def get_weather(
        self,
        season: int,
        grand_prix: str,
        session_name: str,
    ) -> pd.DataFrame:
        session = self.get_session_metadata(season, grand_prix, session_name)
        if not session:
            return pd.DataFrame()
        
        response = requests.get(
            f"{self.BASE_URL}/weather",
            params={"session_key": session["session_key"]},
            timeout=30,
        )
        
        response.raise_for_status()
        
        return pd.DataFrame(response.json())