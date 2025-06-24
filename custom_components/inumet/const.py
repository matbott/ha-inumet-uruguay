"""Constants for the Inumet integration."""
from datetime import timedelta

DOMAIN = "inumet"
NAME = "Inumet Uruguay"
VERSION = "2.0.0"

# URLs de la API
ALERTS_URL = "https://w2b.inumet.gub.uy/oapi/collections/urn:wmo:md:uy-inumet:cap-alerts/items?f=json"
STATIONS_URL = "https://w2b.inumet.gub.uy/oapi/collections/stations/items?limit=100"
JOBS_URL = "https://w2b.inumet.gub.uy/oapi/jobs"
JOB_RESULTS_URL_TEMPLATE = "https://w2b.inumet.gub.uy/oapi/jobs/{job_id}/results"

# Intervalo de actualización (cada 10 minutos)
UPDATE_INTERVAL = timedelta(minutes=10)
