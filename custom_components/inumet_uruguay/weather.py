"""Weather platform for Inumet Uruguay."""
from __future__ import annotations
from typing import Any

from homeassistant.components.weather import (
    Forecast,
    WeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN, NAME, VERSION
from .coordinator import InumetDataUpdateCoordinator

# Mapeo de IDs de Zona a Nombres de Zona del pronóstico
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

    def __init__(self, coordinator: InumetDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the weather entity."""
        super().__init__(coordinator)
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
    
    def _get_today_forecast(self) -> dict | None:
        """Helper to get the forecast for today for the selected station's zone."""
        forecast_data = self.coordinator.data.get("forecast", {})
        if not forecast_data:
            return None

        # Simplificación para encontrar la zona de la estación
        station_zone_name = None
        if "Metropolitana" in self.station_name or "Carrasco" in self.station_name:
            station_zone_name = "Área Metropolitana"
        elif "Punta del Este" in self.station_name:
            station_zone_name = "Punta del este"
        # ... aquí irían más mapeos para otras zonas
        
        if not station_zone_name:
            # Fallback si no hay mapeo: usar la primera zona del pronóstico
            station_zone_name = forecast_data.get("items", [{}])[0].get("zonaLarga", "")

        zone_id = ZONE_MAP.get(station_zone_name)
        if not zone_id:
            return None

        for item in forecast_data.get("items", []):
            if item.get("zonaId") == zone_id and item.get("diaMasN") == 0:
                return item # Devuelve el pronóstico de hoy para la zona correcta
        
        return None

    @property
    def condition(self) -> str | None:
        """Return the current condition from today's forecast."""
        today_forecast = self._get_today_forecast()
        if today_forecast:
            return CONDITION_MAP.get(str(today_forecast.get("estadoTiempo")))
        return None

    @property
    def native_temperature(self) -> float | None:
        """Return the temperature from today's forecast max."""
        today_forecast = self._get_today_forecast()
        if today_forecast:
            return today_forecast.get("tempMax")
        return None

    # Las siguientes propiedades no las podemos obtener de forma fiable, así que las eliminamos
    # de la entidad principal para que no muestren "Desconocido".
    @property
    def humidity(self) -> float | None:
        return None
    @property
    def native_pressure(self) -> float | None:
        return None
    @property
    def native_wind_speed(self) -> float | None:
        return None
    @property
    def wind_bearing(self) -> float | None:
        return None

    async def async_forecast_daily(self) -> list[Forecast] | None:
        """Return the daily forecast."""
        # Esta función es similar a _get_today_forecast pero para todos los días
        forecast_data = self.coordinator.data.get("forecast", {})
        if not forecast_data:
            return None
        
        # Lógica para encontrar la zona (copiada de arriba)
        station_zone_name = None
        if "Metropolitana" in self.station_name or "Carrasco" in self.station_name:
            station_zone_name = "Área Metropolitana"
        elif "Punta del Este" in self.station_name:
            station_zone_name = "Punta del este"
        
        if not station_zone_name:
            station_zone_name = forecast_data.get("items", [{}])[0].get("zonaLarga", "")
        
        zone_id = ZONE_MAP.get(station_zone_name)
        if not zone_id:
            return None
            
        forecasts = []
        # La API no da una fecha completa, así que la construimos nosotros
        start_date = dt_util.parse_date(forecast_data.get("inicioPronostico"))

        for item in forecast_data.get("items", []):
            if item.get("zonaId") == zone_id:
                day_offset = item.get("diaMasN", 0)
                forecast_date = start_date + timedelta(days=day_offset)
                
                forecast = {
                    "datetime": forecast_date.isoformat(),
                    "native_temperature": item.get("tempMax"),
                    "native_templow": item.get("tempMin"),
                    "condition": CONDITION_MAP.get(str(item.get("estadoTiempo"))),
                }
                forecasts.append(forecast)
        
        return forecasts
