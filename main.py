from src.cli_parser import CLIParser
from src.dimensions.geo_ip_extractor import GeoIpExtractor
from src.dimensions.user_agent_extractor import UserAgentExtractor
from src.line_separators.apache_log_line_separator import ApacheLogLineSeparator
from src.log_parsers.log_parser import LogParser
from src.repositories.geoip_databases.geolite2_database import GeoLite2Database


def main():
    print("Hello from adaptive6-hw!")
    cli_arguments = CLIParser().parse()
    file_path = cli_arguments.file_path
    print(f"Log File Path: {file_path}")
    log_type = cli_arguments.log_type
    print(f"Log Type: {log_type}")

    match log_type.lower():
        case "apache":
            geolite_database = GeoLite2Database()
            res = LogParser(
                ApacheLogLineSeparator(),
                [GeoIpExtractor(geolite_database), UserAgentExtractor()],
            ).parse_file(cli_arguments.file_path)
            print(res)
        case _:
            raise ValueError(f"Unsupported log type: {log_type}")



if __name__ == "__main__":
    main()
