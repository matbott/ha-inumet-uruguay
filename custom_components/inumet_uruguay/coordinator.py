"""DataUpdateCoordinator for Inumet Uruguay."""
# ... (las importaciones no cambian) ...
from .const import (
    DOMAIN,
    ALERTS_URL,
    FORECAST_URL,
    ESTADO_ACTUAL_URL,
    NAME,
)

_LOGGER = logging.getLogger(__package__)

class InumetDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from Inumet API."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.config_entry = entry  # Guardamos la entrada de config
        self.station_id = entry.data["station_id"]
        self.station_name = entry.title
        self.session = async_get_clientsession(hass)
        
        # --- LÓGICA MODIFICADA: Leer el intervalo de la config ---
        # Leemos el intervalo de las opciones (si existen) o de los datos iniciales.
        update_interval_minutes = entry.options.get("update_interval", entry.data.get("update_interval"))
        update_interval = timedelta(minutes=update_interval_minutes)
        
        super().__init__(
            hass,
            _LOGGER,
            name=f"{NAME} ({self.station_name})",
            update_interval=update_interval,  # Usamos el intervalo configurado
        )

    # El resto del archivo _fetch_data y _async_update_data no necesita cambios.
    # ...
