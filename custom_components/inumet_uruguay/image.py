"""Image platform for Inumet Uruguay."""
from __future__ import annotations
from datetime import datetime

from homeassistant.components.image import ImageEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN, NAME, VERSION
from .coordinator import InumetDataUpdateCoordinator

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the image platform."""
    coordinator: InumetDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([InumetMapImage(coordinator, entry)])


class InumetMapImage(CoordinatorEntity[InumetDataUpdateCoordinator], ImageEntity):
    """Inumet Map Image Entity."""

    _attr_content_type = "image/png"
    _attr_has_entity_name = True
    _attr_name = "Mapa de Alertas"

    def __init__(self, coordinator: InumetDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the image entity."""
        super().__init__(coordinator)
        self.station_name = entry.data["station_name"]
        self._attr_unique_id = f"{entry.entry_id}_alert_map"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"{NAME} - {self.station_name}",
            manufacturer="matbott",
            sw_version=VERSION,
            model="Estación Meteorológica",
        )

    @property
    def image_url(self) -> str | None:
        """Return the URL of the image."""
        adv_gral_data = self.coordinator.data.get("adv_gral", {})
        return adv_gral_data.get("mapaMerge")

    @property
    def image_last_updated(self) -> datetime | None:
        """Return the last time the image was updated."""
        adv_gral_data = self.coordinator.data.get("adv_gral", {})
        if date_str := adv_gral_data.get("fechaActualizacion"):
            # Aseguramos que la fecha tenga información de zona horaria
            return dt_util.parse_datetime(date_str).astimezone(dt_util.UTC)
        return None
