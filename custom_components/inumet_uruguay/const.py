"""Constants for the Inumet Uruguay integration."""
from datetime import timedelta

DOMAIN = "inumet_uruguay"
NAME = "Inumet Uruguay"
MANUFACTURER = "matbott & 🤖"
VERSION = "3.3.9"

# URLs de la API
ESTADO_ACTUAL_URL = "https://www.inumet.gub.uy/reportes/estadoActual/datos_inumet_ui_publica.mch"
ALERTS_URL = "https://w2b.inumet.gub.uy/oapi/collections/urn:wmo:md:uy-inumet:cap-alerts/items?f=json"
FORECAST_URL = "https://www.inumet.gub.uy/reportes/pronosticos/pronosticoV4.json"
GENERAL_ALERTS_URL = "https://inumet.gub.uy/reportes/riesgo/advGral.mch" # <-- URL NUEVA
ALERTS_CHECK_URL = "https://www.inumet.gub.uy/admin/check-avisos"

# Intervalo de actualización
DEFAULT_UPDATE_INTERVAL = 30

# Constantes para la configuración
CONF_STATION_ID = "station_id"
CONF_STATION_NAME = "station_name"
CONF_UPDATE_INTERVAL = "update_interval"
