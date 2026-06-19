"""Interface for GeoIP databases that resolve an IP address to a country name."""

from abc import ABC, abstractmethod


class GeoIPDatabase(ABC):
    """Resolves IP addresses to country names.

    Concrete implementations (e.g. ``GeoLite2Database``) decide how the
    underlying data is sourced and looked up.
    """

    @abstractmethod
    def get_country_name_from_ip(self, ip_address: str) -> str | None:
        """Return the country name for ``ip_address``, or None if unresolved."""
        ...
