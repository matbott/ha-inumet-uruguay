"""Binary sensor platform for Inumet Uruguay."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, NAME, VERSION, MANUFACTURER
# --- 1. LÍNEA MODIFICADA ---
from .coordinator import InumetDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the binary_sensor platform."""
    coordinator: InumetDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([InumetAlertsBinarySensor(coordinator, entry)])


# --- 2. LÍNEA MODIFICADA ---
class InumetAlertsBinarySensor(CoordinatorEntity[InumetDataUpdateCoordinator], BinarySensorEntity):
    """Inumet Alerts binary_sensor class."""

    _attr_has_entity_name = True
    _attr_name = "Alerta"  # Nombre específico para esta entidad
    _attr_device_class = BinarySensorDeviceClass.SAFETY

    # --- 3. LÍNEA MODIFICADA ---
    def __init__(self, coordinator: InumetDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_alerts"

        # La información del dispositivo es la misma para todas las entidades
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"{NAME} - {entry.data['station_name']}",
            manufacturer=MANUFACTURER,
            sw_version=VERSION,
            model="Estación Meteorológica",
            entry_type="service",
        )

    @property
    def is_on(self) -> bool:
        """Return true if there are active alerts."""
        # Ahora los datos de alertas están dentro de la clave 'alerts'
        alerts_data = self.coordinator.data.get("alerts", {})
        return alerts_data and len(alerts_data.get("features", [])) > 0

    @property
    def extra_state_attributes(self) -> dict | None:
        """Return the state attributes."""
        if not self.is_on:
            return None

        alerts_list = []
        alerts_data = self.coordinator.data.get("alerts", {})
        for alert_feature in alerts_data.get("features", []):
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
