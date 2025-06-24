"""Constants for the Inumet Uruguay integration."""
from datetime import timedelta

DOMAIN = "inumet_uruguay"
NAME = "Inumet Uruguay"
VERSION = "2.0.0"

# URLs de la API
ALERTS_URL = "https://w2b.inumet.gub.uy/oapi/collections/urn:wmo:md:uy-inumet:cap-alerts/items?f=json"
STATIONS_URL = "https://w2b.inumet.gub.uy/oapi/collections/stations/items?limit=100"
JOBS_URL = "https://w2b.inumet.gub.uy/oapi/jobs"
JOB_RESULTS_URL_TEMPLATE = "https://w2b.inumet.gub.uy/oapi/jobs/{job_id}/results"
# URL base del pronóstico, sin el parámetro de cache
FORECAST_URL = "https://www.inumet.gub.uy/reportes/pronosticos/pronosticoV4.json"

# Intervalo de actualización
UPDATE_INTERVAL = timedelta(minutes=15)
