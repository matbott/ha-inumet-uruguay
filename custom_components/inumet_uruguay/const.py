"""Constants for the Inumet Uruguay integration."""
from datetime import timedelta

DOMAIN = "inumet_uruguay"
NAME = "Inumet Uruguay"
VERSION = "3.0.3"

# URLs de la API
ESTADO_ACTUAL_URL = "https://www.inumet.gub.uy/reportes/estadoActual/datos_inumet_ui_publica.mch"
ALERTS_URL = "https://w2b.inumet.gub.uy/oapi/collections/urn:wmo:md:uy-inumet:cap-alerts/items?f=json"
FORECAST_URL = "https://www.inumet.gub.uy/reportes/pronosticos/pronosticoV4.json"

# --- LÍNEA MODIFICADA ---
# Intervalo de actualización por defecto en minutos
DEFAULT_UPDATE_INTERVAL = 15
