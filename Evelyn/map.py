import requests
import folium
import webbrowser
from geopy.geocoders import Nominatim

def get_coordinates(location):
    """Gets latitude and longitude using Nominatim (OpenStreetMap)."""
    geolocator = Nominatim(user_agent="myGeocoder")
    try:
        location = geolocator.geocode(location)
        if location:
            return (location.latitude, location.longitude)
        else:
            print(f"Could not find coordinates for {location}")
            return None
    except Exception as e:
        print(f"Error fetching coordinates for {location}: {e}")
        return None

def get_route(origin_coords, destination_coords):
    """Gets the route and distance using OSRM API."""
    try:
        osrm_url = f"http://router.project-osrm.org/route/v1/driving/{origin_coords[1]},{origin_coords[0]};{destination_coords[1]},{destination_coords[0]}?overview=full&geometries=geojson"
        response = requests.get(osrm_url).json()

        if "routes" in response and response["routes"]:
            route = response["routes"][0]["geometry"]["coordinates"]
            distance_km = response["routes"][0]["distance"] / 1000  # Convert meters to km
            return distance_km, route
        else:
            print("Error: Could not retrieve route")
            return None, None
    except Exception as e:
        print(f"Error fetching route: {e}")
        return None, None

def create_map(route_coordinates, origin, destination):
    """Creates a map with a route plotted between two locations."""
    start_lat, start_lon = route_coordinates[0][1], route_coordinates[0][0]
    end_lat, end_lon = route_coordinates[-1][1], route_coordinates[-1][0]

    m = folium.Map(location=[(start_lat + end_lat) / 2, (start_lon + end_lon) / 2], zoom_start=10)

    # Add markers
    folium.Marker([start_lat, start_lon], popup=f"Start: {origin}", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker([end_lat, end_lon], popup=f"Destination: {destination}", icon=folium.Icon(color="red")).add_to(m)

    # Add the route
    folium.PolyLine([(coord[1], coord[0]) for coord in route_coordinates], color="blue", weight=5).add_to(m)

    # Save and open map
    map_file = "route_map.html"
    m.save(map_file)
    webbrowser.open(map_file)

def GMAPS(origin, destination):
    """Calculates distance and generates a map."""
    origin_coords = get_coordinates(origin)
    destination_coords = get_coordinates(destination)

    if not origin_coords or not destination_coords:
        print("Error: Could not find one or both locations.")
        return

    distance, route_coordinates = get_route(origin_coords, destination_coords)
    if distance is None or route_coordinates is None:
        print("Error calculating route.")
        return

    print(f"The distance between {origin} and {destination} is: {distance:.2f} km")
    create_map(route_coordinates, origin, destination)

if __name__ == "__main__":
    origin = input("Enter the starting location: ")
    destination = input("Enter the destination: ")
    GMAPS(origin, destination)




