"""Config flow for Inumet Alerts."""
from __future__ import annotations

from homeassistant.config_entries import ConfigFlow
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, NAME

class InumetAlertsFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Inumet Alerts."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        # Solo permitir una única instancia de esta integración
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(title=NAME, data={})

        return self.async_show_form(step_id="user")