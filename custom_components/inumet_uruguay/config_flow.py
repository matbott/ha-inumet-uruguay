"""Config flow for Inumet Uruguay."""
from __future__ import annotations
from typing import Any
import httpx
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, ESTADO_ACTUAL_URL, DEFAULT_UPDATE_INTERVAL

class InumetFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Inumet Uruguay."""

    VERSION = 1
    
    def __init__(self) -> None:
        """Initialize the config flow."""
        self.station_options: dict[int, str] = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the user step."""
        # --- LÓGICA AÑADIDA: Limitar a 3 instancias ---
        if len(self._async_current_entries()) >= 3:
            return self.async_abort(reason="max_instances_reached")

        errors: dict[str, str] = {}

        if user_input is not None:
            station_id = user_input["station_id"]
            station_name = self.station_options.get(station_id, "Estación Desconocida")
            
            data_to_save = {
                "station_id": station_id,
                "station_name": station_name,
                "update_interval": user_input["update_interval"],
            }
            
            return self.async_create_entry(title=station_name, data=data_to_save)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(ESTADO_ACTUAL_URL, timeout=10)
                response.raise_for_status()
                data = response.json()
            
            station_options = {
                station["id"]: station["nombre"]
                for station in data["estaciones"]
                if station.get("gerencia") == "INUMET"
            }
            self.station_options = dict(sorted(station_options.items(), key=lambda item: item[1]))

        except httpx.HTTPError:
            errors["base"] = "cannot_connect"
        except Exception:
            errors["base"] = "unknown"

        if errors:
            return self.async_show_form(step_id="user", errors=errors)

        # --- LÓGICA MODIFICADA: Añadir campo de intervalo al formulario ---
        data_schema = vol.Schema(
            {
                vol.Required("station_id"): vol.In(self.station_options),
                vol.Required(
                    "update_interval", default=DEFAULT_UPDATE_INTERVAL
                ): vol.All(vol.Coerce(int), vol.Range(min=30, max=240)),
            }
        )
        
        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> OptionsFlowHandler:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle an options flow."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            # Actualiza las opciones en la entrada de configuración
            return self.async_create_entry(title="", data=user_input)

        # Muestra el formulario de opciones
        schema = vol.Schema(
            {
                vol.Required(
                    "update_interval",
                    default=self.config_entry.options.get(
                        "update_interval",
                        self.config_entry.data.get("update_interval", DEFAULT_UPDATE_INTERVAL),
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=30, max=240)),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
