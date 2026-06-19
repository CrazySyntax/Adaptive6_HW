"""Reads a MaxMind GeoLite2 Country IPv4 blocks CSV into a network -> country map.

The GeoLite2 ``Blocks`` CSV does not contain country names, only the numeric
``registered_country_geoname_id``. We resolve those ids to human-readable
country names via the ``geonamescache`` library, whose country records expose
the same GeoNames id under the ``geonameid`` key.
"""

import csv
from pathlib import Path

import geonamescache


class GeoIPDatabase:
    """Loads the GeoLite2 Country blocks CSV and maps each network to a country."""

    def __init__(self, csv_path: str | Path) -> None:
        self._csv_path = Path(csv_path)
        self._geoname_id_to_country = self._build_geoname_id_index()

    @staticmethod
    def _build_geoname_id_index() -> dict[str, str]:
        """Map GeoNames id (as string) -> country name using geonamescache."""
        countries = geonamescache.GeonamesCache().get_countries()
        return {str(country["geonameid"]): country["name"] for country in countries.values()}

    def load(self) -> dict[str, str]:
        """Return ``{network: country_name}`` for every resolvable row in the CSV.

        Rows whose ``registered_country_geoname_id`` is blank or cannot be
        resolved to a country name are skipped.
        """
        if not self._csv_path.is_file():
            raise FileNotFoundError(f"GeoIP CSV not found: {self._csv_path}")

        network_to_country: dict[str, str] = {}
        with self._csv_path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                geoname_id = row["registered_country_geoname_id"].strip()
                country = self._geoname_id_to_country.get(geoname_id)
                if country is not None:
                    network_to_country[row["network"]] = country
        return network_to_country
