from src.repositories.geoip_databases.geolite2_database import GeoLite2Database


def main():
    print("Hello from adaptive6-hw!")
    g = GeoLite2Database()
    print(g.get_country_name_from_ip("83.149.9.216"))

if __name__ == "__main__":
    main()
