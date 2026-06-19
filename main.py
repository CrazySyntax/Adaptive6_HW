from src.file_parser import FileParser
from src.line_separators.apache_log_line_separator import ApacheLogLineSeparator
from src.repositories.geoip_databases.geolite2_database import GeoLite2Database


def main():
    print("Hello from adaptive6-hw!")
    g = GeoLite2Database()
    print(g.get_country_name_from_ip("83.149.9.216"))
    iter = FileParser(ApacheLogLineSeparator()).parse_file("./resources/apache_log.txt")
    for line in iter:
        print(line)
    print("end")

if __name__ == "__main__":
    main()
