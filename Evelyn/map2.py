import openrouteservice

# Replace 'YOUR_API_KEY' with your actual API key
ors_client = openrouteservice.Client(key="5b3ce3597851110001cf624803593088dbb84f409848303b12d78378")  

def get_coordinates(location):
    try:
        geocode = ors_client.pelias_search(location)
        if not geocode or len(geocode['features']) == 0:
            print(f"Could not find coordinates for {location}")
            return None
        return geocode['features'][0]['geometry']['coordinates']  # Returns [longitude, latitude]
    except Exception as e:
        print(f"Error fetching coordinates for {location}: {e}")
        return None

def get_distance(origin, destination):
    origin_coords = get_coordinates(origin)
    destination_coords = get_coordinates(destination)

    if not origin_coords or not destination_coords:
        return None

    try:
        route = ors_client.directions(
            coordinates=[origin_coords, destination_coords],
            profile="driving-car",
            format="geojson"
        )

        distance_km = route['features'][0]['properties']['segments'][0]['distance'] / 1000
        return distance_km  # Returns distance in kilometers
    except Exception as e:
        print(f"Error calculating distance: {e}")
        return None

def GMAPS(origin, destination):
    distance = get_distance(origin, destination)
    if distance is None:
        print("Error calculating distance.")
        return
    
    print(f"The distance between {origin} and {destination} is: {distance:.2f} km")

if __name__ == "__main__":
    origin = input("Enter the starting location: ")
    destination = input("Enter the destination: ")
    GMAPS(origin, destination)


import openrouteservice
import folium
import webbrowser

# Replace with your actual API key
ors_client = openrouteservice.Client(key="your_actual_api_key_here")

def get_coordinates(location):
    """Fetches coordinates (latitude, longitude) for a given location."""
    try:
        geocode = ors_client.pelias_search(location)
        if not geocode or len(geocode['features']) == 0:
            print(f"Could not find coordinates for {location}")
            return None
        return geocode['features'][0]['geometry']['coordinates']  # [longitude, latitude]
    except Exception as e:
        print(f"Error fetching coordinates for {location}: {e}")
        return None

def get_route(origin, destination):
    """Fetches the route and calculates the distance between two locations."""
    origin_coords = get_coordinates(origin)
    destination_coords = get_coordinates(destination)

    if not origin_coords or not destination_coords:
        return None, None

    try:
        route = ors_client.directions(
            coordinates=[origin_coords, destination_coords],
            profile="driving-car",
            format="geojson"
        )

        distance_km = route['features'][0]['properties']['segments'][0]['distance'] / 1000
        route_coordinates = route['features'][0]['geometry']['coordinates']  # Route path

        return distance_km, route_coordinates
    except Exception as e:
        print(f"Error calculating route: {e}")
        return None, None

def create_map(route_coordinates, origin, destination):
    """Creates a map with a route plotted between two locations."""
    start_lat, start_lon = route_coordinates[0][1], route_coordinates[0][0]  # Convert [lon, lat] to [lat, lon]
    end_lat, end_lon = route_coordinates[-1][1], route_coordinates[-1][0]

    m = folium.Map(location=[(start_lat + end_lat) / 2, (start_lon + end_lon) / 2], zoom_start=10)

    # Add markers for start and end points
    folium.Marker([start_lat, start_lon], popup=f"Start: {origin}", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker([end_lat, end_lon], popup=f"Destination: {destination}", icon=folium.Icon(color="red")).add_to(m)

    # Add the route line
    folium.PolyLine([(coord[1], coord[0]) for coord in route_coordinates], color="blue", weight=5).add_to(m)

    # Save and open the map
    map_file = "route_map.html"
    m.save(map_file)
    webbrowser.open(map_file)  # Open map in browser

def GMAPS(origin, destination):
    """Calculates distance and generates a map."""
    distance, route_coordinates = get_route(origin, destination)
    if distance is None or route_coordinates is None:
        print("Error calculating route.")
        return

    print(f"The distance between {origin} and {destination} is: {distance:.2f} km")

    # Create and open map
    create_map(route_coordinates, origin, destination)

if __name__ == "__main__":
    origin = input("Enter the starting location: ")
    destination = input("Enter the destination: ")
    GMAPS(origin, destination)
