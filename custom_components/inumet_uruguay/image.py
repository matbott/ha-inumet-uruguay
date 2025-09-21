"""Image platform for Inumet Uruguay."""
from __future__ import annotations
from dataclasses import dataclass
from collections.abc import Callable
import logging
from datetime import datetime

from homeassistant.components.image import ImageEntity, ImageEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN, NAME, VERSION, MANUFACTURER
from .coordinator import InumetDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

def _get_alert_map_url(data: dict | None) -> str | None:
    """Safely generate the alert map URL with a cache buster."""
    if not data or not (base_url := data.get("adv_gral", {}).get("mapaMerge")):
        return None

    if last_updated := data.get("last_updated_timestamp"):
        timestamp = int(last_updated.timestamp())
        
        if "?" in base_url:
            return f"{base_url}&v={timestamp}"
        else:
            return f"{base_url}?v={timestamp}"

    return base_url

def _get_fwi_url_data() -> tuple[str, datetime]:
    """Generate URL and updated time for the FWI map."""
    now = dt_util.now()
    date_str = now.strftime('%Y_%m_%d')
    url = f"https://www.inumet.gub.uy/reportes/fwi/FWI_{date_str}.png"
    return url, dt_util.start_of_local_day(now)

def _get_uv_url_data(data: dict | None) -> tuple[str | None, datetime | None]:
    """Get URL and updated time for the UV map."""
    if not data or not (url := data.get("latest_uv_url")):
        return None, None
    try:
        parts = url.split('_')
        date_part = parts[-2]
        time_part = parts[-1].split('.')[0]
        
        naive_dt = datetime.strptime(f"{date_part}{time_part}", "%Y%j%H%M")
        utc_dt = dt_util.as_utc(naive_dt)
        local_dt = dt_util.as_local(utc_dt)
        return url, local_dt

    except (IndexError, ValueError):
        return url, None


@dataclass(frozen=True, kw_only=True)
class InumetImageEntityDescription(ImageEntityDescription):
    """Describes a Inumet image entity."""
    key: str
    name: str
    icon: str
    url_fn: Callable[[dict | None], str | None] | None = None
    last_updated_fn: Callable[[dict | None], datetime | None] | None = None


IMAGE_DESCRIPTIONS: tuple[InumetImageEntityDescription, ...] = (
    InumetImageEntityDescription(
        key="alert_map", name="Mapa de Alertas", icon="mdi:alert-outline",
        url_fn=_get_alert_map_url,
        last_updated_fn=lambda data: dt_util.parse_datetime(data.get("adv_gral", {}).get("fechaActualizacion")) if data and data.get("adv_gral", {}).get("fechaActualizacion") else None,
    ),
    InumetImageEntityDescription(
        key="fwi_map", name="Mapa de Peligro de Incendio (FWI)", icon="mdi:fire",
        url_fn=lambda data: _get_fwi_url_data()[0],
        last_updated_fn=lambda data: _get_fwi_url_data()[1],
    ),
    # --- INICIO DE LA CORRECCIÓN ---
    InumetImageEntityDescription(
        key="uv_map", name="Mapa de Índice UV", icon="mdi:sun-wireless-outline",
        # Le volvemos a añadir el [0] para que tome solo la URL del resultado
        url_fn=lambda data: _get_uv_url_data(data)[0],
        last_updated_fn=lambda data: _get_uv_url_data(data)[1],
    ),
    # --- FIN DE LA CORRECCIÓN ---
)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up the image platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        InumetImage(hass, coordinator, entry, description) for description in IMAGE_DESCRIPTIONS
    )

class InumetImage(CoordinatorEntity[InumetDataUpdateCoordinator], ImageEntity):
    """Inumet Image Entity."""
    entity_description: InumetImageEntityDescription
    _attr_has_entity_name = True

    def __init__(self, hass: HomeAssistant, coordinator: InumetDataUpdateCoordinator, entry: ConfigEntry, description: InumetImageEntityDescription) -> None:
        """Initialize the image entity."""
        super().__init__(coordinator)
        ImageEntity.__init__(self, hass) 
        
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_name = description.name
        self._attr_icon = description.icon
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"{NAME} ({entry.title})",
            manufacturer=MANUFACTURER,
            sw_version=VERSION,
            model="Estación Meteorológica",
        )
    
    @property
    def device_class(self) -> str | None:
        """Return the device class of the image."""
        return None 

    @property
    def image_url(self) -> str | None:
        """Return the URL of the image."""
        if self.entity_description.url_fn:
            return self.entity_description.url_fn(self.coordinator.data)
        return None

    @property
    def image_last_updated(self) -> datetime | None:
        """Return the last time the image was updated."""
        if self.coordinator.data and self.entity_description.last_updated_fn:
            try:
                return self.entity_description.last_updated_fn(self.coordinator.data)
            except (ValueError, TypeError):
                return None
        return None
