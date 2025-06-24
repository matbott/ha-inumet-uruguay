"""Weather platform for Inumet Uruguay."""
from __future__ import annotations
from typing import Any

from homeassistant.components.weather import (
    Forecast,
    WeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.const import (
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, NAME, VERSION
from .coordinator import InumetDataUpdateCoordinator

# Mapeo de IDs de Zona a Nombres de Zona del pronóstico
# Esto puede necesitar ser expandido o mejorado en el futuro
ZONE_MAP = {
    "Área Metropolitana": 88,
    "Este": 68,
    "Centro-Sur": 67,
    "Suroeste": 86,
    "Noroeste": 66,
    "Noreste": 65,
    "Punta del este": 89,
}

# Mapeo de iconos del pronóstico de Inumet a los de Home Assistant
CONDITION_MAP = {
    "1": "sunny",
    "2": "partlycloudy",
    "3": "partlycloudy",
    "4": "cloudy",
    "5": "cloudy",
    "6": "cloudy",
    "7": "rainy",
    "8": "fog",
    "9": "partlycloudy",
    "10": "lightning",
    "11": "lightning-rainy",
    "12": "windy",
    "13": "cloudy",
    "14": "fog",
    "15": "fog",
    "16": "fog",
    "17": "snowy",
    "18": "exceptional",
    "19": "windy-variant",
    "20": "clear-night",
    "21": "partlycloudy",
    "22": "partlycloudy",
    "23": "rainy",
    "24": "cloudy",
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the weather platform."""
    coordinator: InumetDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([InumetWeather(coordinator, entry)])


class InumetWeather(CoordinatorEntity[InumetDataUpdateCoordinator], WeatherEntity):
    """Inumet Weather Entity."""

    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_wind_speed_unit = UnitOfSpeed.METERS_PER_SECOND

    def __init__(self, coordinator: InumetDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the weather entity."""
        super().__init__(coordinator)
        self.station_name = entry.data["station_name"]
        self._attr_unique_id = f"{entry.entry_id}_weather"
        self._attr_name = self.station_name
        self._attr_supported_features = (
            WeatherEntityFeature.FORECAST_DAILY
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"{NAME} - {self.station_name}",
            manufacturer="matbott",
            sw_version=VERSION,
            model="Estación Meteorológica",
            entry_type="service",
        )
    
    def _get_weather_prop(self, key: str) -> Any | None:
        """Helper to get a property from the weather data."""
        return self.coordinator.data.get("weather", {}).get(key, {}).get("value")

    @property
    def condition(self) -> str | None:
        """Return the current condition."""
        # Aquí podríamos mapear la condición actual si la tuviéramos
        return None  # Por ahora no tenemos un icono del tiempo actual fiable

    @property
    def native_temperature(self) -> float | None:
        """Return the temperature."""
        return self._get_weather_prop("air_temperature")

    @property
    def native_pressure(self) -> float | None:
        """Return the pressure."""
        return self._get_weather_prop("pressure_reduced_to_mean_sea_level")

    @property
    def humidity(self) -> float | None:
        """Return the humidity."""
        return self._get_weather_prop("relative_humidity")

    @property
    def native_wind_speed(self) -> float | None:
        """Return the wind speed."""
        return self._get_weather_prop("wind_speed")

    @property
    def wind_bearing(self) -> float | None:
        """Return the wind bearing."""
        return self._get_weather_prop("wind_direction")

    async def async_forecast_daily(self) -> list[Forecast] | None:
        """Return the daily forecast."""
        forecast_data = self.coordinator.data.get("forecast", {})
        if not forecast_data:
            return None
        
        # Necesitamos encontrar la zona del pronóstico para nuestra estación
        # Esto es una simplificación, en el futuro podría mejorarse
        station_zone_name = None
        if "Metropolitana" in self.station_name or "Carrasco" in self.station_name:
            station_zone_name = "Área Metropolitana"
        elif "Punta del Este" in self.station_name:
            station_zone_name = "Punta del este"
        # ... aquí irían más mapeos
        
        if not station_zone_name:
             # Si no encontramos mapeo, usamos la primera zona como fallback
            station_zone_name = forecast_data.get("items", [{}])[0].get("zonaLarga", "")

        
        zone_id = ZONE_MAP.get(station_zone_name)
        if not zone_id:
            return None
            
        forecasts = []
        for item in forecast_data.get("items", []):
            if item.get("zonaId") == zone_id:
                forecast = {
                    "datetime": item.get("grupo"), # La API no da fecha completa por día
                    "native_temperature": item.get("tempMax"),
                    "native_templow": item.get("tempMin"),
                    "condition": CONDITION_MAP.get(str(item.get("estadoTiempo"))),
                }
                forecasts.append(forecast)
        
        return forecasts
