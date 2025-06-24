"""Config flow for Inumet Uruguay."""
from __future__ import annotations

import httpx
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, STATIONS_URL


class InumetFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Inumet Uruguay."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the user step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        errors = {}
        
        if user_input is not None:
            # El usuario ha seleccionado una estación, creamos la entrada
            # user_input['station_id'] contiene el ID, ej: "0-20000-0-86580"
            # user_input[CONF_NAME] contiene el nombre, ej: "Carrasco"
            return self.async_create_entry(
                title=user_input[CONF_NAME], data=user_input
            )

        # Si no hay input, mostramos el formulario
        try:
            # Hacemos una llamada a la API para obtener las estaciones
            async with httpx.AsyncClient() as client:
                response = await client.get(STATIONS_URL, timeout=10)
                response.raise_for_status()
                stations_data = response.json()
            
            # Creamos un diccionario con ID: Nombre para el dropdown
            stations_dict = {
                station["properties"]["wigos_station_identifier"]: station["properties"]["name"]
                for station in stations_data["features"]
            }

        except httpx.HTTPError:
            errors["base"] = "cannot_connect"
        except Exception:
            errors["base"] = "unknown"

        # Creamos el esquema del formulario si tenemos estaciones
        if not errors:
            schema = vol.Schema(
                {
                    vol.Required(CONF_NAME): vol.In(stations_dict),
                }
            )
            # Revertimos el diccionario para poder buscar el nombre por ID
            schema = vol.Schema(
                {
                    vol.Required("station_id"): vol.In({v: k for k, v in stations_dict.items()}),
                }
            )
            # Volvemos a invertir para la selección final
            station_map = {v: k for k, v in stations_dict.items()}
            
            schema = vol.Schema(
                {
                    vol.Required(CONF_NAME): vol.In(list(stations_dict.values()))
                }
            )
            
            # Map para el dropdown: {ID: Nombre}
            station_options = {
                station["properties"]["wigos_station_identifier"]: station["properties"]["name"]
                for station in stations_data["features"]
            }

            # Ordenamos alfabéticamente por nombre de estación
            sorted_station_options = dict(sorted(station_options.items(), key=lambda item: item[1]))

            data_schema = vol.Schema(
                {
                    vol.Required("station_id"): vol.In(sorted_station_options),
                }
            )
            
            return self.async_show_form(
                step_id="user", data_schema=data_schema, errors=errors
            )

        # Si hubo un error al obtener las estaciones, lo mostramos
        return self.async_show_form(step_id="user", errors=errors)
