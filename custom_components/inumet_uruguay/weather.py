"""Weather platform for Inumet Uruguay."""
from __future__ import annotations
from datetime import timedelta

from homeassistant.components.weather import (
    Forecast,
    WeatherEntity,
    WeatherEntityFeature,
    ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TEMP_LOW,
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_TIME,
)
from homeassistant.const import UnitOfTemperature, UnitOfSpeed, UnitOfPressure
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN, NAME, VERSION
from .coordinator import InumetDataUpdateCoordinator

# Mapeo de iconos del pronóstico de Inumet a los de Home Assistant
CONDITION_MAP = {
    "1": "sunny", "2": "partlycloudy", "3": "partlycloudy", "4": "cloudy",
    "5": "cloudy", "6": "cloudy", "7": "rainy", "8": "fog", "9": "partlycloudy",
    "10": "lightning", "11": "lightning-rainy", "12": "windy", "13": "cloudy",
    "14": "fog", "15": "fog", "16": "fog", "17": "snowy", "18": "exceptional",
    "19": "windy-variant", "20": "clear-night", "21": "partlycloudy",
    "22": "partlycloudy", "23": "rainy", "24": "cloudy",
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
    _attr_native_wind_speed_unit = UnitOfSpeed.KNOTS # La API entrega en nudos

    def __init__(self, coordinator: InumetDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the weather entity."""
        super().__init__(coordinator)
        self.station_id = entry.data["station_id"]
        self.station_name = entry.data["station_name"]
        
        self._attr_unique_id = f"{entry.entry_id}_weather"
        self._attr_name = self.station_name
        self._attr_supported_features = WeatherEntityFeature.FORECAST_DAILY
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"{NAME} - {self.station_name}",
            manufacturer="matbott",
            sw_version=VERSION,
            model="Estación Meteorológica",
        )

    def _get_current_observation(self, variable_id_str: str):
        """Helper para obtener un valor de la matriz de observaciones."""
        try:
            estado_data = self.coordinator.data["estado"]
            station_idx = next((i for i, est in enumerate(estado_data["estaciones"]) if est["id"] == self.station_id), None)
            variable_idx = next((i for i, var in enumerate(estado_data["variables"]) if var["idStr"] == variable_id_str), None)
            
            if station_idx is not None and variable_idx is not None:
                return estado_data["observaciones"][variable_idx]["datos"][station_idx][-1]
            return None
        except (KeyError, IndexError, TypeError):
            return None

    @property
    def condition(self) -> str | None:
        """Return the current condition."""
        # La API de estado actual no provee un icono del tiempo, así que lo dejamos vacío.
        return None

    @property
    def native_temperature(self) -> float | None:
        """Return the temperature."""
        return self._get_current_observation("TempAire")

    @property
    def native_pressure(self) -> float | None:
        """Return the pressure."""
        return self._get_current_observation("PresAtmMar")

    @property
    def humidity(self) -> float | None:
        """Return the humidity."""
        return self._get_current_observation("HumRelativa")

    @property
    def native_wind_speed(self) -> float | None:
        """Return the wind speed."""
        return self._get_current_observation("IntViento")

    @property
    def wind_bearing(self) -> float | None:
        """Return the wind bearing."""
        return self._get_current_observation("DirViento")

    async def async_forecast_daily(self) -> list[Forecast] | None:
        """Return the daily forecast."""
        forecast_data = self.coordinator.data.get("forecast", {})
        if not forecast_data or not forecast_data.get("items"):
            return None
        
        # Lógica para encontrar la zona del pronóstico
        # Podríamos hacer esto más inteligente en el futuro, por ahora es una aproximación
        station_data = next((est for est in self.coordinator.data["estado"]["estaciones"] if est["id"] == self.station_id), None)
        zone_id = station_data.get("estado") if station_data else None

        if not zone_id:
            return None

        forecasts = []
        start_date = dt_util.parse_date(forecast_data.get("inicioPronostico"))
        
        for item in forecast_data.get("items", []):
            if item.get("zonaCorta") == zone_id:
                day_offset = item.get("diaMasN", 0)
                forecast_date = start_date + timedelta(days=day_offset)
                
                forecast = {
                    ATTR_FORECAST_TIME: forecast_date.isoformat(),
                    ATTR_FORECAST_TEMP: item.get("tempMax"),
                    ATTR_FORECAST_TEMP_LOW: item.get("tempMin"),
                    ATTR_FORECAST_CONDITION: CONDITION_MAP.get(str(item.get("estadoTiempo"))),
                }
                forecasts.append(forecast)
        
        return forecasts
