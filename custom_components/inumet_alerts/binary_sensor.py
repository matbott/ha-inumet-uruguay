"""Binary sensor platform for Inumet Alerts."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, NAME
from .coordinator import InumetAlertsDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([InumetAlertsBinarySensor(coordinator)])


class InumetAlertsBinarySensor(CoordinatorEntity[InumetAlertsDataUpdateCoordinator], BinarySensorEntity):
    """Inumet Alerts binary_sensor class."""

    _attr_name = NAME
    _attr_device_class = BinarySensorDeviceClass.SAFETY
    _attr_has_entity_name = True

    def __init__(self, coordinator: InumetAlertsDataUpdateCoordinator) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_alerts"

    @property
    def is_on(self) -> bool:
        """Return true if there are active alerts."""
        return self.coordinator.data and len(self.coordinator.data.get("features", [])) > 0

    @property
    def extra_state_attributes(self) -> dict | None:
        """Return the state attributes."""
        if not self.is_on:
            return None

        alerts_list = []
        for alert_feature in self.coordinator.data["features"]:
            properties = alert_feature.get("properties", {})
            alert_info = {
                "id": properties.get("id"),
                "titulo": properties.get("event"),
                "severidad": properties.get("severity"),
                "certeza": properties.get("certainty"),
                "descripcion": properties.get("description"),
                "areas_afectadas": properties.get("areaDesc"),
                "inicio": properties.get("effective"),
                "expira": properties.get("expires"),
                "instrucciones": properties.get("instruction"),
            }
            alerts_list.append(alert_info)

        return {
            "cantidad_alertas": len(alerts_list),
            "alertas": alerts_list,
            "ultima_actualizacion": self.coordinator.last_update_success_time,
        }