"""DataUpdateCoordinator for Inumet Uruguay."""
from __future__ import annotations
import logging
import asyncio

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    ALERTS_URL,
    JOBS_URL,
    JOB_RESULTS_URL_TEMPLATE,
    UPDATE_INTERVAL,
    NAME,
)

_LOGGER = logging.getLogger(__package__)

class InumetDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from Inumet API."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.station_id = entry.data["station_id"]
        self.session = async_get_clientsession(hass)
        super().__init__(
            hass,
            _LOGGER,
            name=f"{NAME} ({entry.data['station_name']})",
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_get_weather_data(self) -> dict:
        """Fetch the latest weather data via the jobs endpoint."""
        # Paso 1: Obtener la lista de jobs
        response = await self.session.get(JOBS_URL)
        response.raise_for_status()
        jobs_data = await response.json()

        # Paso 2: Encontrar el job más reciente, exitoso y relevante
        latest_job_id = None
        for job in jobs_data.get("jobs", []):
            if job.get("ProcessID") == "bufr2geojson" and job.get("Status") == "successful":
                latest_job_id = job.get("JobID")
                break  # Encontramos el más reciente, salimos del bucle

        if not latest_job_id:
            _LOGGER.warning("No successful 'bufr2geojson' job found.")
            return {}

        # Paso 3: Obtener los resultados de ese job
        results_url = JOB_RESULTS_URL_TEMPLATE.format(job_id=latest_job_id)
        response = await self.session.get(results_url)
        response.raise_for_status()
        results_data = await response.json()
        
        # Paso 4: Procesar y filtrar los datos para nuestra estación
        station_weather = {}
        for item in results_data.get("items", []):
            properties = item.get("properties", {})
            if properties.get("wigos_station_identifier") == self.station_id:
                measurement_name = properties.get("name")
                # Guardamos el diccionario completo de propiedades
                station_weather[measurement_name] = properties
        
        return station_weather

    async def _async_get_alerts_data(self) -> dict:
        """Fetch alerts data."""
        response = await self.session.get(ALERTS_URL)
        response.raise_for_status()
        return await response.json()

    async def _async_update_data(self) -> dict:
        """Fetch data from API endpoint."""
        try:
            # Hacemos las dos llamadas a la API en paralelo para más eficiencia
            results = await asyncio.gather(
                self._async_get_weather_data(),
                self._async_get_alerts_data(),
            )
            return {"weather": results[0], "alerts": results[1]}
        except Exception as exception:
            raise UpdateFailed(f"Error communicating with API: {exception}") from exception
