"""DataUpdateCoordinator for Inumet Uruguay."""
from __future__ import annotations
import logging  # <-- LA LÍNEA QUE FALTABA
import asyncio
from datetime import datetime

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    ALERTS_URL,
    FORECAST_URL,
    ESTADO_ACTUAL_URL,
    NAME,
)

_LOGGER = logging.getLogger(__package__)

class InumetDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from Inumet API."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.config_entry = entry
        self.station_id = entry.data["station_id"]
        self.station_name = entry.title
        self.session = async_get_clientsession(hass)
        
        # Leemos el intervalo de las opciones (si existen) o de los datos iniciales.
        update_interval_minutes = entry.options.get("update_interval", entry.data.get("update_interval"))
        update_interval = timedelta(minutes=update_interval_minutes)
        
        super().__init__(
            hass,
            _LOGGER,
            name=f"{NAME} ({self.station_name})",
            update_interval=update_interval,
        )

    async def _fetch_data(self, url: str) -> dict:
        """Generic data fetcher."""
        if "pronosticoV4.json" in url:
            cache_buster = datetime.now().strftime("%Y-%m-%d-%H-%M")
            url = f"{url}?{cache_buster}"
        
        response = await self.session.get(url)
        response.raise_for_status()
        return await response.json()

    async def _async_update_data(self) -> dict:
        """Fetch all data from API endpoints."""
        try:
            results = await asyncio.gather(
                self._fetch_data(ESTADO_ACTUAL_URL),
                self._fetch_data(ALERTS_URL),
                self._fetch_data(FORECAST_URL),
            )
            return {"estado": results[0], "alerts": results[1], "forecast": results[2]}
        except Exception as exception:
            raise UpdateFailed(f"Error communicating with API: {exception}") from exception
