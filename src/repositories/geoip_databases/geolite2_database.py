"""Reads a MaxMind GeoLite2 Country IPv4 blocks CSV into a network -> country map.

The GeoLite2 ``Blocks`` CSV does not contain country names, only the numeric
``registered_country_geoname_id``. We resolve those ids to human-readable
country names via the ``geonamescache`` library, whose country records expose
the same GeoNames id under the ``geonameid`` key.
"""

import csv
import ipaddress
from pathlib import Path

import geonamescache

from src.config import GEOLITE2_CSV_PATH
from src.repositories.geoip_databases.geoip_database import GeoIPDatabase


class GeoLite2Database(GeoIPDatabase):
    """Loads the GeoLite2 Country blocks CSV and maps each network to a country."""

    def __init__(self) -> None:
        self._csv_path = Path(GEOLITE2_CSV_PATH)
        self._geoname_id_to_country = self._build_geoname_id_index()
        self._network_to_country: dict[str, str] | None = None

    def get_country_name_from_ip(self, ip_address: str) -> str | None:
        """Return the country name for ``ip_address``, or None if unresolved.

        The CSV is loaded once on first call and cached. NOTE: this scans every
        network (O(n) per lookup); the GeoLite2 CSV has ~583K rows, so a
        longest-prefix lookup structure is still needed before this is used at
        scale (see CLAUDE.md).
        """
        if self._network_to_country is None:
            self._network_to_country = self.load()
        for network, country in self._network_to_country.items():
            if self.ip_matches_network(ip_address, network):
                return country
        return None

    # NOTE: kept as a non-static instance method by project convention — see CLAUDE.md.
    def ip_matches_network(self, ip_address: str, network: str) -> bool:
        """Return True if ``ip_address`` falls within the CIDR ``network``.

        ``network`` is a CIDR string carrying the subnet mask as a prefix
        length, e.g. ``"1.0.0.0/24"`` (the format used in the GeoLite2 CSV's
        ``network`` column). Returns False if either argument is malformed.
        """
        try:
            address = ipaddress.ip_address(ip_address)
            subnet = ipaddress.ip_network(network, strict=False)
        except ValueError:
            return False
        return address in subnet

    def _build_geoname_id_index(self) -> dict[str, str]:
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
