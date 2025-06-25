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
    
    def __init__(self) -> None:
        """Initialize the config flow."""
        self.station_options: dict[int, str] = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the user step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        errors: dict[str, str] = {}

        # --- LÓGICA CORREGIDA ---
        if user_input is not None:
            # El usuario ha enviado el formulario, tenemos el 'station_id'.
            station_id = user_input["station_id"]
            # Usamos el diccionario que guardamos en la instancia para encontrar el nombre.
            station_name = self.station_options.get(station_id, "Estación Desconocida")
            
            # Preparamos los datos para guardar.
            data_to_save = {
                "station_id": station_id,
                "station_name": station_name,
            }
            
            # Creamos la entrada de configuración.
            return self.async_create_entry(title=station_name, data=data_to_save)

        # Si no hay input del usuario, obtenemos las estaciones y mostramos el formulario.
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(ESTADO_ACTUAL_URL, timeout=10)
                response.raise_for_status()
                data = response.json()
            
            # Creamos y guardamos el diccionario de estaciones en la instancia.
            station_options = {
                station["id"]: station["nombre"]
                for station in data["estaciones"]
                if station.get("gerencia") == "INUMET"
            }
            # Guardamos las opciones ordenadas por nombre para usarlas después.
            self.station_options = dict(sorted(station_options.items(), key=lambda item: item[1]))

        except httpx.HTTPError:
            errors["base"] = "cannot_connect"
            # Si hay un error, nos aseguramos de que no se muestre un formulario roto.
            self.station_options = {}
        except Exception:
            errors["base"] = "unknown"
            self.station_options = {}

        # Si hubo errores al obtener la lista, los mostramos sin el formulario.
        if errors:
            return self.async_show_form(step_id="user", errors=errors)

        # Si todo fue bien, creamos el esquema del formulario con las estaciones.
        data_schema = vol.Schema(
            {
                vol.Required("station_id"): vol.In(self.station_options),
            }
        )
        
        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
