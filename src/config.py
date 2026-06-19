"""Centralized access to environment variables, loaded from a ``.env`` file.

``load_dotenv()`` reads the project ``.env`` once at import time, so every
module can rely on ``os.environ`` being populated. Real environment variables
always take precedence over values in ``.env``.
"""

import os

from dotenv import load_dotenv

load_dotenv()

# Path to the MaxMind GeoLite2 Country IPv4 blocks CSV.
GEOLITE2_CSV_PATH = os.getenv("GEOLITE2_CSV_PATH", "db/GeoLite2-Country-Blocks-IPv4.csv")
