"""Extracts the Country dimension from a parsed log line via IP geolocation."""

from src.dimensions.dimension_extractor import DimensionExtractor
from src.repositories.geoip_databases.geoip_database import GeoIPDatabase

# Position of the client IP address within a parsed Apache log line.
_DEFAULT_IP_FIELD_INDEX = 0


class GeoIpExtractor(DimensionExtractor):
    """Resolves the country name from the IP address field of a log line."""

    def __init__(self, geoip_database: GeoIPDatabase, ip_field_index: int = _DEFAULT_IP_FIELD_INDEX) -> None:
        self._geoip_database = geoip_database
        self._ip_field_index = ip_field_index
        # IP -> country name (or None) cache. The underlying database lookup is
        # an O(n) scan over ~583K networks; logs repeat the same IPs heavily, so
        # caching each result (misses included) avoids re-scanning per line.
        self._ip_to_country: dict[str, str | None] = {}

    def extract(self, fields: list[str]) -> str | None:
        """Return the country for the line's IP address, or None if unresolved."""
        if self._ip_field_index >= len(fields):
            return None
        ip_address = fields[self._ip_field_index]
        if ip_address not in self._ip_to_country:
            self._ip_to_country[ip_address] = self._geoip_database.get_country_name_from_ip(ip_address)
            return self._ip_to_country[ip_address]
        else:
            return self._ip_to_country[ip_address]
