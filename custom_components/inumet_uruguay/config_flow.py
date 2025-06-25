"""Config flow for Inumet Uruguay."""
from __future__ import annotations
from typing import Any
import httpx
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, ESTADO_ACTUAL_URL

class InumetFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Inumet Uruguay."""
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the user step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        errors: dict[str, str] = {}

        if user_input is not None:
            return self.async_create_entry(title=user_input["station_name"], data=user_input)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(ESTADO_ACTUAL_URL, timeout=10)
                response.raise_for_status()
                data = response.json()
            
            station_options = {
                station["id"]: station["nombre"]
                for station in data["estaciones"]
                if station.get("gerencia") == "INUMET" # Filtramos solo las de INUMET
            }
            sorted_station_options = dict(sorted(station_options.items(), key=lambda item: item[1]))
        except Exception:
            errors["base"] = "cannot_connect"
            sorted_station_options = {}

        data_schema = vol.Schema({vol.Required("station_id"): vol.In(sorted_station_options)})
        
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)
