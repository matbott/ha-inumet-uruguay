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

        # --- LÓGICA MEJORADA ---
        # Recorremos los jobs recientes hasta encontrar datos para nuestra estación
        for job in jobs_data.get("jobs", []):
            if job.get("ProcessID") == "bufr2geojson" and job.get("Status") == "successful":
                # Encontramos un job relevante, ahora vemos si tiene nuestros datos
                job_id = job.get("JobID")
                results_url = JOB_RESULTS_URL_TEMPLATE.format(job_id=job_id)
                
                _LOGGER.debug("Revisando job %s para la estación %s", job_id, self.station_id)
                
                res_response = await self.session.get(results_url)
                # Usamos continue para saltar a la siguiente iteración si este job falla
                if res_response.status != 200:
                    continue
                
                results_data = await res_response.json()

                station_weather = {}
                # Buscamos si alguno de los items en este job es de nuestra estación
                for item in results_data.get("items", []):
                    properties = item.get("properties", {})
                    if properties.get("wigos_station_identifier") == self.station_id:
                        measurement_name = properties.get("name")
                        station_weather[measurement_name] = properties
                
                # Si encontramos datos para nuestra estación, los devolvemos y terminamos
                if station_weather:
                    _LOGGER.info("Datos encontrados para la estación %s en el job %s", self.station_id, job_id)
                    return station_weather

        # Si recorrimos todos los jobs y no encontramos nada, avisamos y devolvemos vacío
        _LOGGER.warning("No se encontraron datos recientes para la estación %s", self.station_id)
        return {}
        # --- FIN DE LA LÓGICA MEJORADA ---

    async def _async_get_alerts_data(self) -> dict:
        """Fetch alerts data."""
        response = await self.session.get(ALERTS_URL)
        response.raise_for_status()
        return await response.json()

    async def _async_update_data(self) -> dict:
        """Fetch data from API endpoint."""
        try:
            results = await asyncio.gather(
                self._async_get_weather_data(),
                self._async_get_alerts_data(),
            )
            return {"weather": results[0], "alerts": results[1]}
        except Exception as exception:
            raise UpdateFailed(f"Error communicating with API: {exception}") from exception
