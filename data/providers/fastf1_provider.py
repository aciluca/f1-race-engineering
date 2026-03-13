from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import fastf1
import pandas as pd

from data.providers.base import BaseSessionProvider


logger = logging.getLogger(__name__)


class FastF1Provider(BaseSessionProvider):
    def __init__(self, cache_dir: Path) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        fastf1.Cache.enable_cache(str(self.cache_dir))

    def provider_name(self) -> str:
        return "fastf1"

    def _load_session(self, season: int, grand_prix: str, session_name: str):
        logger.info(
            "Loading FastF1 session: season=%s grand_prix=%s session=%s",
            season,
            grand_prix,
            session_name,
        )
        session = fastf1.get_session(season, grand_prix, session_name)
        session.load()
        return session

    def get_event_schedule(self, season: int) -> pd.DataFrame:
        logger.info("Loading event schedule for season=%s", season)
        schedule = fastf1.get_event_schedule(season)
        logger.info("Event schedule loaded: rows=%s", len(schedule))
        return schedule

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
        laps_df = pd.DataFrame(session.laps)

        logger.info(
            "Laps loaded: rows=%s columns=%s",
            len(laps_df),
            list(laps_df.columns),
        )
        return laps_df

    def get_telemetry(
        self,
        season: int,
        grand_prix: str,
        session_name: str,
        driver_code: str,
        lap_number: int | None = None,
    ) -> pd.DataFrame:
        session = self._load_session(season, grand_prix, session_name)

        driver_laps = session.laps.pick_drivers(driver_code)
        logger.info("Driver laps loaded for %s: rows=%s", driver_code, len(driver_laps))

        if driver_laps.empty:
            logger.warning("No laps found for driver=%s", driver_code)
            return pd.DataFrame()

        if "LapTime" in driver_laps.columns:
            driver_laps = driver_laps.dropna(subset=["LapTime"])
            logger.info("Valid laps after LapTime filtering for %s: rows=%s", driver_code, len(driver_laps))

        if driver_laps.empty:
            logger.warning("No valid laps with LapTime for driver=%s", driver_code)
            return pd.DataFrame()

        if lap_number is not None:
            selected_laps = driver_laps[driver_laps["LapNumber"] == lap_number]
            if selected_laps.empty:
                logger.warning(
                    "No lap found for driver=%s lap_number=%s",
                    driver_code,
                    lap_number,
                )
                return pd.DataFrame()
            lap = selected_laps.iloc[0]
            logger.info("Using requested lap_number=%s for driver=%s", lap_number, driver_code)
        else:
            lap = driver_laps.pick_fastest()
            logger.info(
                "Using fastest lap for driver=%s lap_number=%s lap_time=%s",
                driver_code,
                lap["LapNumber"] if "LapNumber" in lap.index else "N/A",
                lap["LapTime"] if "LapTime" in lap.index else "N/A",
            )

        telemetry = lap.get_car_data().add_distance()
        telemetry_df = pd.DataFrame(telemetry)

        logger.info(
            "Telemetry loaded for %s: rows=%s columns=%s",
            driver_code,
            len(telemetry_df),
            list(telemetry_df.columns),
        )

        return telemetry_df

    def get_weather(
        self,
        season: int,
        grand_prix: str,
        session_name: str,
    ) -> pd.DataFrame:
        session = self._load_session(season, grand_prix, session_name)
        weather_df = pd.DataFrame(session.weather_data)
        logger.info("Weather loaded: rows=%s", len(weather_df))
        return weather_df
