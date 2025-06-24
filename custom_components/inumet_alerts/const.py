"""Constants for the Inumet Alerts integration."""
from datetime import timedelta

DOMAIN = "inumet_alerts"
NAME = "Inumet Alertas"

# URL directa a los items de alertas
ALERTS_URL = "https://w2b.inumet.gub.uy/oapi/collections/urn:wmo:md:uy-inumet:cap-alerts/items?f=json"

# Intervalo de actualización (cada 15 minutos)
UPDATE_INTERVAL = timedelta(minutes=15)