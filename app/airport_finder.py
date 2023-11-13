import json
from geopy.distance import geodesic


class AirportFinder:
    def __init__(self, airports_json='utils/airports.json'):
        self.json_file = airports_json
        self.airports_coords = self.parse_airports_coords()

    def parse_airports_coords(self):
        airports = {}
        with open(self.json_file, 'r', encoding='utf-8') as f:
            json_string = f.readline()
            airports_list = json.loads(json_string)

        for airport in airports_list:
            if airport['iata_type'] == 'airport':
                airports[airport['code']] = {
                    'lat': airport['coordinates']['lat'],
                    'lon': airport['coordinates']['lon']
                }
        return airports

    def find_nearest_airport(self, user_coordinates):
        nearest_airport = None
        min_distance = float("inf")

        for airport_name, coords in self.airports_coords.items():
            airport_coordinates = (coords['lat'], coords['lon'])
            distance = geodesic(user_coordinates, airport_coordinates).kilometers
            if distance < min_distance:
                min_distance = distance
                nearest_airport = airport_name
        return nearest_airport


airports_finder = AirportFinder()

if __name__ == '__main__':
    airports_json_file = 'airports.json'
    user_coords = (59.984078, 30.385342)
    print(airports_finder.find_nearest_airport(user_coords))