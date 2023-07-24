import re
import requests
import json
import folium
import random
from urllib.parse import urlparse, parse_qs
from collections import defaultdict

def get_random_color():
    colors = ['blue', 'green', 'lightblue', 'yellow', 'purple', 'gray', 'black', 'darkgreen', 'lime', 'olive', 'cyan']
    return random.choice(colors)

def create_marker_icon(name):
    icon_html = f"""
        <div style="text-align: center; font-weight: bold; font-size: 12px; background-color: white; padding: 4px;
                    width: {len(name) * 10}px;">
            {name}
        </div>
    """
    return folium.DivIcon(html=icon_html)

def create_legend(map_object, data, num_red_connections, num_routes):
    legend_html = """
    <div style="
        position: fixed; 
        top: 10px;
        right: 10px;
        z-index: 1000;
        padding: 10px;
        background-color: white;
        border-radius: 5px;
        border: 2px solid gray;
        font-size: 12px;
        ">
        <h4>Airlines</h4>
        <table>
            <tbody>
    """
    for name, color in data.items():
        num_routes_for_airline = num_routes[name]
        legend_html += f"""
            <tr>
                <td><span style="background:{color}; width: 16px; height: 16px; display: inline-block;"></span></td>
                <td>{name} ({num_routes_for_airline} Routes)</td>
            </tr>
        """

    legend_html += f"""
            <tr>
                <td><span style="background:red; width: 16px; height: 16px; display: inline-block;"></span></td>
                <td>Bad connections ({num_red_connections})</td>
            </tr>
        """

    legend_html += """
            </tbody>
        </table>
    </div>
    """

    map_object.get_root().html.add_child(folium.Element(legend_html))
 
def compare_json_data(data):
    # defaultdict, um die Anzahl der Vorkommen der Dateien zu zählen
    file_counts = defaultdict(int)

    # Durchlaufen der JSON-Daten und Zählen der Vorkommen jeder Datei
    for name, routes in data.items():
        for route in routes:
            dep_file = route["dep"]
            des_file = route["des"]
            file_counts[dep_file] += 1
            file_counts[des_file] += 1

    # Filtern der Dateien, die mindestens zweimal vorkommen
    return {file: count for file, count in file_counts.items() if count >= 2}

def extract_info_from_webpages(urls):
    try:
        all_extracted_info = {}
        all_route_counts = {}
        name_connections = defaultdict(set)
        airline_colors = {}
        num_red_connections = 0
        num_routes = defaultdict(int)  # Wird zum Zählen der Routen für jede Airline verwendet
        
        def get_airline_name(url):
            query_string = parse_qs(urlparse(url).query)
            return query_string.get('cs', ['UNKNOWN'])[0]

        for url in urls:
            # Webseite herunterladen
            response = requests.get(url)
            if response.status_code != 200:
                print(f"Fehler beim Abrufen der Webseite: {url}")
                continue

            # Den Quellcode der Webseite erhalten
            webpage_source = response.text

            # Name der Webseite aus der URL extrahieren
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            name = query_params.get('cs', ['Unknown'])[0]

            # Regulärer Ausdruck zum Extrahieren der Informationen
            pattern = r'{"dep_lat":"([^"]*)","dep_lon":"([^"]*)","des_lat":"([^"]*)","des_lon":"([^"]*)","dep":"([^"]*)","des":"([^"]*)"}'

            extracted_info_list = []
            matches = re.finditer(pattern, webpage_source)
            for match in matches:
                extracted_info = {
                    "dep_lat": float(match.group(1)),
                    "dep_lon": float(match.group(2)),
                    "des_lat": float(match.group(3)),
                    "des_lon": float(match.group(4)),
                    "dep": match.group(5),
                    "des": match.group(6)
                }
                extracted_info_list.append(extracted_info)

                # Zähle die Anzahl der Routen pro Namen
                all_route_counts[name] = all_route_counts.get(name, 0) + 1

            if extracted_info_list:
                # Informationen in das all_extracted_info-Dictionary speichern
                if name not in all_extracted_info:
                    all_extracted_info[name] = []
                all_extracted_info[name].extend(extracted_info_list)
                
                print(f"{len(extracted_info_list)} Routen wurden von Webseite '{name}' gefunden.")
            else:
                print(f"Die gewünschten Informationen konnten in Webseite '{name}' nicht gefunden werden.")        

        # Karte erstellen
        map_center = [48.8588443, 2.2943506]  # Koordinaten für die Kartenmitte (hier: Paris)
        my_map = folium.Map(location=map_center, zoom_start=5)

        # Farben für jede Airline setzen und Routen zählen
        for name in all_extracted_info.keys():
            airline_colors[name] = get_random_color()

        # Linien auf der Karte zeichnen und Namen mit Schild hervorheben
        legend_data = {}
        for name, data in all_extracted_info.items():
            for route in data:
                start_point = (route["dep_lat"], route["dep_lon"])
                end_point = (route["des_lat"], route["des_lon"])

                # Linie auf der Karte zeichnen
                connection_key = frozenset([route['dep'], route['des']])
                name_connections[connection_key].add(name)

                # Hinzufügen der Verbindung in umgekehrter Richtung
                reverse_connection_key = frozenset([route['des'], route['dep']])
                name_connections[reverse_connection_key].add(name)

                if len(name_connections[connection_key]) >= 2 or len(name_connections[reverse_connection_key]) >= 2:
                    color = 'red'
                    num_red_connections += 1
                else:
                    color = airline_colors[name]

                folium.PolyLine(locations=[start_point, end_point], color=color).add_to(my_map)

                # Marker mit Schild für "dep" hinzufügen
                folium.Marker(start_point, icon=create_marker_icon(route['dep'])).add_to(my_map)

                # Marker mit Schild für "des" hinzufügen
                folium.Marker(end_point, icon=create_marker_icon(route['des'])).add_to(my_map)

                legend_data[name] = color
                num_routes[name] += 1

        # Legende auf der Karte hinzufügen
        create_legend(my_map, legend_data, num_red_connections, num_routes)

        # Karte in eine HTML-Datei speichern
        my_map.save("map.html")

        print("Karte wurde in 'map.html' gespeichert.")
    except Exception as e:
        print(f"Fehler: {e}")

    # Linien, die in mindestens zwei Namen gespeichert sind, rot färben
    for connection_key, names in name_connections.items():
        if len(names) >= 2:
            print(f"Verbindung {connection_key} wird von {len(names)} Airlines geteilt: {names}")

    # Ausgabe des name_connections-Dictionarys
    print("name_connections:")
    for connection_key, names in name_connections.items():
        print(f"{connection_key}: {names}")

# Beispielaufruf des Programms mit einer Liste von Webseiten
urls = [
    "https://flylat.net/flylat_connect/map/index.php?t=r&cs=AVA",
    "https://flylat.net/flylat_connect/map/index.php?t=r&cs=ARCA",
    "https://flylat.net/flylat_connect/map/index.php?t=r&cs=ANZ",
    "https://flylat.net/flylat_connect/map/index.php?t=r&cs=LI",
    "https://flylat.net/flylat_connect/map/index.php?t=r&cs=RYR",
    "https://flylat.net/flylat_connect/map/index.php?t=r&cs=HRN"
    
    # Füge hier weitere URLs hinzu, falls erforderlich
]
extract_info_from_webpages(urls)