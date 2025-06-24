"""Sensor platform for Inumet Uruguay."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
    DEGREE
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, NAME, VERSION
from .coordinator import InumetDataUpdateCoordinator

# Definimos cada sensor que queremos crear
ENTITY_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="air_temperature",
        name="Temperatura",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="relative_humidity",
        name="Humedad Relativa",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="pressure_reduced_to_mean_sea_level",
        name="Presión",
        device_class=SensorDeviceClass.ATMOSPHERIC_PRESSURE,
        native_unit_of_measurement=UnitOfPressure.HPA,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="wind_speed",
        name="Velocidad del Viento",
        device_class=SensorDeviceClass.WIND_SPEED,
        native_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:weather-windy",
    ),
    SensorEntityDescription(
        key="wind_direction",
        name="Dirección del Viento",
        device_class=SensorDeviceClass.WIND_DIRECTION,
        native_unit_of_measurement=DEGREE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:compass-outline",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the sensor platform."""
    coordinator: InumetDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    # Creamos un sensor por cada descripción en la lista de arriba
    async_add_entities(
        InumetWeatherSensor(coordinator, entry, description)
        for description in ENTITY_DESCRIPTIONS
    )


class InumetWeatherSensor(CoordinatorEntity[InumetDataUpdateCoordinator], SensorEntity):
    """Inumet Weather Sensor class."""

    def __init__(
        self,
        coordinator: InumetDataUpdateCoordinator,
        entry: ConfigEntry,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = description
        
        # Atributos de la entidad
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

        # Se asocia al mismo dispositivo que el sensor de alertas
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"{NAME} - {entry.data['station_name']}",
            manufacturer="matbott",
            sw_version=VERSION,
            model="Estación Meteorológica",
            entry_type="service",
        )

    @property
    def native_value(self) -> float | None:
        """Return the native value of the sensor."""
        # Buscamos el dato en la estructura del coordinador
        # ej: data['weather']['air_temperature']['value']
        weather_data = self.coordinator.data.get("weather", {})
        measurement = weather_data.get(self.entity_description.key, {})
        return measurement.get("value")
