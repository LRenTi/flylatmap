import folium
import json
from branca.element import Template, MacroElement
import os

def create_site(id):
    path = f'data/routes/{id}.json'
    
    with open(path, 'r') as f:
        data = json.load(f)

    routelist = data.get('routes', [])
    airline_name = data.get('name', '')
    airline_id = data.get('id', '')

    m = folium.Map(location=[0, 0], zoom_start=2)

    count_routes = 0
    count_missing_routes = 0

    for route in routelist:
        departure_info = route.get('departure', {})
        destination_info = route.get('destination', {})
        if isinstance(departure_info, dict) and isinstance(destination_info, dict):
            departure_lat = departure_info.get('latitude')
            departure_lon = departure_info.get('longitude')
            destination_lat = destination_info.get('latitude')
            destination_lon = destination_info.get('longitude')
            if departure_lat is not None and departure_lon is not None and destination_lat is not None and destination_lon is not None:
                count_routes = count_routes + 1
                folium.Marker(
                    location=[departure_lat, departure_lon],
                    popup=f"{departure_info.get('name', 'Unknown')} ({departure_info.get('ICAO', 'Unknown')})",
                    icon=folium.Icon(color='blue')
                ).add_to(m)
                folium.Marker(
                    location=[destination_lat, destination_lon],
                    popup=f"{destination_info.get('name', 'Unknown')} ({destination_info.get('ICAO', 'Unknown')})",
                    icon=folium.Icon(color='blue')
                ).add_to(m)
                folium.PolyLine(
                    [(departure_lat, departure_lon), (destination_lat, destination_lon)],
                    smooth_factor=50,
                    tooltip=f"({departure_info.get('ICAO', 'Unknown')}) - ({destination_info.get('ICAO', 'Unknown')})", 
                    color="grey"
                ).add_to(m)
            else:
                count_missing_routes = count_missing_routes + 1
                print("Skipping route with missing or invalid coordinates")
        else:
            count_missing_routes = count_missing_routes + 1
            print("Skipping route with missing or invalid airport information")

    filename = f'{id}.html'
    folder = 'maps/'
    os.mkdir(folder)
    path = folder + filename
    m.save(path)
    
    print(count_routes, "Routes added to the map.")
    if count_missing_routes > 0:
        print(count_missing_routes, "Routes could not be added to the map due to missing or invalid coordinates.")
    print(f"Map saved to {path}")
