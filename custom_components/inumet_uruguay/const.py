"""Constants for the Inumet Uruguay integration."""
from datetime import timedelta

DOMAIN = "inumet_uruguay"
NAME = "Inumet Uruguay"
VERSION = "3.0.0" # ¡Nueva versión mayor!

# La URL principal que contiene todos los datos del estado actual
ESTADO_ACTUAL_URL = "https://www.inumet.gub.uy/reportes/estadoActual/datos_inumet_ui_publica.mch"

# La URL de alertas sigue siendo útil y fiable
ALERTS_URL = "https://w2b.inumet.gub.uy/oapi/collections/urn:wmo:md:uy-inumet:cap-alerts/items?f=json"

# La URL del pronóstico también es correcta
FORECAST_URL = "https://www.inumet.gub.uy/reportes/pronosticos/pronosticoV4.json"

# Intervalo de actualización
UPDATE_INTERVAL = timedelta(minutes=10)
