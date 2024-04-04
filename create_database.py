import requests
import json
from tqdm import tqdm
import os
import time
from dotenv import load_dotenv

def get_airport_info(icao_code):
    load_dotenv()
    
    apiToken = os.getenv('API_TOKEN')
    ICAO = icao_code

    url = f"https://airportdb.io/api/v1/airport/{ICAO}?apiToken={apiToken}"

    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if 'name' in data:
            name = data['name']
        else:
            name = None
        if 'latitude_deg' in data:
            latitude = data['latitude_deg']
        else:
            latitude = None
        if 'longitude_deg' in data:
            longitude = data['longitude_deg']
        else:
            longitude = None
        return name, latitude, longitude

def get_Routes(path):
    with open(path, 'r') as f:
        data = json.load(f)
        
        departure_destination_list = data['routes']
        
        newdata = {
            'name': data['name'],
            'id': data['id'],
            'date_last_update:': time.strftime('%d-%m-%Y, %H:%M:%S'),
            'routes': [],
        }
        
        for item in tqdm(departure_destination_list):
            for airport in ['departure', 'destination']:
                if airport in item:
                    icao_code = item[airport]
                    airport_info = get_airport_info(icao_code)
                    if airport_info:
                        name, latitude, longitude = airport_info
                        if latitude is not None and longitude is not None:
                            item[airport] = {
                                'ICAO': icao_code,
                                'name': name,
                                'latitude': latitude,
                                'longitude': longitude
                            }
                        else:
                            item[airport] = {
                                'ICAO': icao_code,
                                'name': name,
                                'latitude': None,
                                'longitude': None
                            }
                            print(f"\nCould not find coordinates for {icao_code}")
        
        newdata['routes'] = departure_destination_list
        
        newpath = 'Data/' + str(data['id']) + '.json'
        
        with open(newpath, 'w') as f:
            json.dump(newdata, f)