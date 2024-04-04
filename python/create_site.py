import folium
import json
from branca.element import Template, MacroElement

def create_site(id):
    path = f'data/routes/{id}.json'
    
    # Lade die Daten aus der JSON-Datei
    with open(path, 'r') as f:
        data = json.load(f)

    routelist = data.get('routes', [])
    airline_name = data.get('name', '')
    airline_id = data.get('id', '')

    # Erstelle eine Karte
    m = folium.Map(location=[0, 0], zoom_start=2)

    count_routes = 0
    count_missing_routes = 0
    # Füge Marker für die Flughäfen hinzu und verbinde sie mit Polylinien, falls eine Route vorhanden ist
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
                folium.PolyLine([(departure_lat, departure_lon), (destination_lat, destination_lon)], color="red").add_to(m)
            else:
                count_missing_routes = count_missing_routes + 1
                print("Skipping route with missing or invalid coordinates")
        else:
            count_missing_routes = count_missing_routes + 1
            print("Skipping route with missing or invalid airport information")

    filename = f'{id}.html'
    path = f'maps/{filename}'
    m.save(path)
    print(count_routes, "Routen wurden erfolgreich in der Karte hinzugefügt.")
    if count_missing_routes > 0:
        print(count_missing_routes, "Routen konnten nicht hinzugefügt werden, da Koordinaten fehlen oder ungültig sind.")
    print(f"Karte wurde erfolgreich in '{filename}' gespeichert.")
