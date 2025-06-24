"""Config flow for Inumet Uruguay."""
from __future__ import annotations
from typing import Any

import httpx
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, STATIONS_URL


class InumetFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Inumet Uruguay."""

    VERSION = 1
    
    def __init__(self) -> None:
        """Initialize the config flow."""
        self.station_options: dict[str, str] = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the user step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        errors: dict[str, str] = {}

        # --- LÓGICA CORREGIDA ---
        if user_input is not None:
            # El usuario ha enviado el formulario, tenemos el 'station_id'
            station_id = user_input["station_id"]
            # Usamos el diccionario que guardamos para encontrar el nombre
            station_name = self.station_options.get(station_id, "Estación Desconocida")
            
            data_to_save = {
                "station_id": station_id,
                "station_name": station_name,
            }
            
            return self.async_create_entry(title=station_name, data=data_to_save)
        # --- FIN DE LA LÓGICA CORREGIDA ---

        # Si no hay input del usuario, obtenemos las estaciones y mostramos el formulario
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(STATIONS_URL, timeout=10)
                response.raise_for_status()
                stations_data = response.json()
            
            # Creamos y guardamos el diccionario con ID: Nombre
            station_options = {
                station["properties"]["wigos_station_identifier"]: station["properties"]["name"]
                for station in stations_data["features"]
            }
            # Lo ordenamos alfabéticamente por nombre de estación para el menú
            self.station_options = dict(sorted(station_options.items(), key=lambda item: item[1]))

        except httpx.HTTPError:
            errors["base"] = "cannot_connect"
        except Exception:
            errors["base"] = "unknown"

        # Si no hubo errores, mostramos el formulario
        if not errors:
            data_schema = vol.Schema(
                {
                    vol.Required("station_id"): vol.In(self.station_options),
                }
            )
            return self.async_show_form(
                step_id="user", data_schema=data_schema, errors=errors
            )

        # Si hubo errores al obtener la lista, los mostramos
        return self.async_show_form(step_id="user", errors=errors)
