"""DataUpdateCoordinator for Inumet Uruguay."""
from __future__ import annotations
import logging
from datetime import timedelta
import httpx
import asyncio

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN, FORECAST_URL, ESTADO_ACTUAL_URL, NAME, ALERTS_URL, GENERAL_ALERTS_URL
)

_LOGGER = logging.getLogger(__name__)

class InumetDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from Inumet API."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.hass = hass
        self.config_entry = entry
        update_interval_minutes = entry.options.get("update_interval", 30)
        update_interval = timedelta(minutes=update_interval_minutes)
        super().__init__(
            hass, _LOGGER, name=f"{NAME} ({entry.title})", update_interval=update_interval
        )
        self.client = httpx.AsyncClient()

    async def _fetch_data(self, url: str) -> dict | None:
        """Generic data fetcher."""
        try:
            response = await self.client.get(url, timeout=20)
            response.raise_for_status()
            if not response.text: return None
            return response.json()
        except Exception as e:
            _LOGGER.warning(f"Error al obtener o procesar datos de {url}: {e}")
            return None

    async def _async_find_latest_uv_url(self) -> str | None:
        """Find the latest available UV map URL by searching backwards in time."""
        now_utc = dt_util.utcnow()
        for i in range(12):  # Intentamos hasta 2 horas hacia atrás (12 * 10 min)
            check_time = now_utc - timedelta(minutes=i * 10)
            rounded_minute = (check_time.minute // 10) * 10
            time_str = f"{check_time.hour:02d}{rounded_minute:02d}"
            year_str = check_time.strftime('%Y')
            day_of_year_str = check_time.strftime('%j')
            url_to_check = f"https://www.inumet.gub.uy/reportes/indice_uv/iuvcsk_{year_str}{day_of_year_str}_{time_str}.webp"
            try:
                response = await self.client.head(url_to_check, timeout=5)
                if response.status_code == 200:
                    _LOGGER.debug("Última URL de UV encontrada: %s", url_to_check)
                    return url_to_check
            except httpx.RequestError:
                continue # Si hay un error de red, simplemente intentamos con la anterior
        _LOGGER.warning("No se pudo encontrar una URL válida para el mapa UV.")
        return None

    async def _async_update_data(self) -> dict:
        """Fetch all data from API endpoints robustly."""
        _LOGGER.debug("Iniciando actualización de datos de Inumet")
        
        # Obtenemos los datos en paralelo
        estado_data = await self._fetch_data(ESTADO_ACTUAL_URL)
        forecast_data = await self._fetch_data(FORECAST_URL)
        alerts_data = await self._fetch_data(ALERTS_URL)
        adv_gral_data = await self._fetch_data(GENERAL_ALERTS_URL)
        latest_uv_url = await self._async_find_latest_uv_url()

        if not estado_data and not forecast_data:
            raise UpdateFailed("No se pudieron obtener los datos esenciales de Inumet.")
        
        return {
            "estado": estado_data,
            "forecast": forecast_data,
            "alerts": alerts_data,
            "adv_gral": adv_gral_data,
            "latest_uv_url": latest_uv_url,
        }
