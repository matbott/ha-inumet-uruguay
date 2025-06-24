"""DataUpdateCoordinator for Inumet Alerts."""
from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, ALERTS_URL, UPDATE_INTERVAL, NAME


class InumetAlertsDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Inumet alerts data from the API."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize."""
        super().__init__(hass, name=f"{NAME} Coordinator", update_interval=UPDATE_INTERVAL)
        self.session = async_get_clientsession(hass)

    async def _async_update_data(self) -> dict:
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            async with self.session.get(ALERTS_URL) as response:
                response.raise_for_status()
                data = await response.json()
                return data
        except Exception as exception:
            raise UpdateFailed(f"Error communicating with API: {exception}") from exception