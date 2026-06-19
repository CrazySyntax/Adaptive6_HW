from src.dimensions.geo_ip_extractor import GeoIpExtractor
from src.dimensions.user_agent_extractor import UserAgentExtractor
from src.line_separators.apache_log_line_separator import ApacheLogLineSeparator
from src.log_parsers.log_parser import LogParser
from src.repositories.geoip_databases.geolite2_database import GeoLite2Database


def main():
    print("Hello from adaptive6-hw!")
    g = GeoLite2Database()
    print(g.get_country_name_from_ip("83.149.9.216"))
    res = LogParser(
        ApacheLogLineSeparator(),
        [GeoIpExtractor(g), UserAgentExtractor()],
    ).parse_file("./resources/apache_log.txt")
    print(res)

if __name__ == "__main__":
    main()
