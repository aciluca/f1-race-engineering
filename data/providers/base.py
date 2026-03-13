from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import pandas as pd


class BaseSessionProvider(ABC):
    """
    Abstract interface for all data providers.

The application doesn't need to know whether the data comes from FastF1,
OpenF1, or other APIs: it must always use this common interface.
    """
    
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider's name"""
        raise NotImplementedError
    
    @abstractmethod
    def get_event_schedule(self, season: int) -> pd.DataFrame:
        """Return the season's event calendar"""
        raise NotImplementedError
    
    @abstractmethod
    def get_session_metadata(
        self,
        season: int,
        grand_prix: str,
        session_name: str,
    ) -> dict[str, Any]:
        """Return session's metadata"""
        raise NotImplementedError
    
    @abstractmethod
    def get_laps(
        self,
        season: int,
        grand_prix: str,
        session_name: str,
    ) -> pd.DataFrame:
        """Return lap data of session"""
        raise NotImplementedError
    
    @abstractmethod
    def get_telemetry(
        self,
        season: int,
        grand_prix: str,
        session_name: str,
        driver_code: str,
        lap_number: int | None = None,
    ) -> pd.DataFrame:
        """Return a pilot's telemetry"""
        raise NotImplementedError
    
    @abstractmethod
    def get_weather(
        self,
        season: int,
        grand_prix: str,
        session_name: str,
    ) -> pd.DataFrame:
        """Returns weather data for the session."""
        raise NotImplementedError