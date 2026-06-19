"""Reads a MaxMind GeoLite2 Country IPv4 blocks CSV into a network -> country map.

The GeoLite2 ``Blocks`` CSV does not contain country names, only the numeric
``registered_country_geoname_id``. We resolve those ids to human-readable
country names via the ``geonamescache`` library, whose country records expose
the same GeoNames id under the ``geonameid`` key.
"""

import csv
import ipaddress
from collections import defaultdict
from pathlib import Path

import geonamescache

from src.config import GEOLITE2_CSV_PATH
from src.repositories.geoip_databases.geoip_database import GeoIPDatabase


class GeoLite2Database(GeoIPDatabase):
    """Loads the GeoLite2 Country blocks CSV and maps each network to a country."""

    # Prefix lengths >= this value pin the first two octets, so such networks can
    # be indexed by first octet -> second octet for fast lookup.
    _GROUPED_PREFIX_THRESHOLD = 16

    def __init__(self) -> None:
        self._csv_path = Path(GEOLITE2_CSV_PATH)
        self._geoname_id_to_country = self._build_geoname_id_index()
        # Flat map for networks with prefix < 16, which span multiple octet groups.
        self._network_to_country: dict[str, str] = {}
        # Nested map for networks with prefix >= 16: first octet -> second octet
        # -> network CIDR -> country. The two octets are fixed for these prefixes,
        # so an IP can be narrowed to a small candidate set before matching.
        self._network_octet_to_country: dict[str, dict[str, dict[str, str]]] = {}
        self.load()
        print("Finished loading GeoLite2 CSV into memory.")

    def get_country_name_from_ip(self, ip_address: str) -> str | None:
        """Return the country name for ``ip_address``, or None if unresolved.

        Looks first in ``_network_octet_to_country``: the IP's first two octets
        narrow the search to the small set of prefix>=16 networks sharing those
        octets. Only if that misses do we fall back to the flat
        ``_network_to_country`` map (prefix<16 networks, which span multiple
        octet groups and so cannot be octet-indexed).
        """
        octets = ip_address.split(".")
        if len(octets) >= 2:
            candidates = self._network_octet_to_country.get(octets[0], {}).get(octets[1], {})
            for network, country in candidates.items():
                if self.ip_matches_network(ip_address, network):
                    return country

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

    def load(self) -> None:
        """Populate the network maps from every resolvable row in the CSV.

        Networks with a prefix length >= 16 go into ``_network_group_to_country``,
        keyed by first octet -> second octet -> network CIDR. Networks with a
        shorter prefix span multiple octet groups, so they go into the flat
        ``_network_to_country`` map. Rows whose ``registered_country_geoname_id``
        is blank or cannot be resolved to a country name are skipped.
        """
        if not self._csv_path.is_file():
            raise FileNotFoundError(f"GeoIP CSV not found: {self._csv_path}")

        grouped: dict[str, dict[str, dict[str, str]]] = defaultdict(lambda: defaultdict(dict))
        with self._csv_path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                geoname_id = row["registered_country_geoname_id"].strip()
                country = self._geoname_id_to_country.get(geoname_id)
                if country is None:
                    continue
                network = row["network"]
                prefix_length = int(network.split("/")[1])
                if prefix_length >= self._GROUPED_PREFIX_THRESHOLD:
                    first_octet, second_octet = network.split(".")[:2]
                    grouped[first_octet][second_octet][network] = country
                else:
                    self._network_to_country[network] = country

        # Convert defaultdicts to plain dicts so lookups can't create empty groups.
        self._network_octet_to_country = {
            first: {second: networks for second, networks in seconds.items()}
            for first, seconds in grouped.items()
        }
