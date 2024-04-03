import requests
import json
from tqdm import tqdm

def get_airport_coordinates(icao_code):
    url = "https://airport-info.p.rapidapi.com/airport"

    querystring = {"icao":icao_code}
    
    headers = {
        "X-RapidAPI-Key": "59de95f2f9msh50bea0dca7488afp1156c6jsnfc81942ea3dc",
        "X-RapidAPI-Host": "airport-info.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    
    if response.status_code == 200:
        data = response.json()
        if 'name' in data:
            name = data['name']
        else:
            name = None
        if 'latitude' in data:
            latitude = data['latitude']
        else:
            latitude = None
        if 'longitude' in data:
            longitude = data['longitude']
        else:
            longitude = None
        return name, latitude, longitude

def get_Routes(path):
    with open(path, 'r') as f:
        data = json.load(f)
        
        count = 0
        for item in data['routes']:
            count = count + 1
        
        departure_destination_list = data['routes']
        
        newdata = {
            'name': data['name'],
            'id': data['id'],
            'routes': [],
        }
        
        for item in tqdm(departure_destination_list):
            for airport_type in ['departure', 'destination']:
                if airport_type in item:
                    icao_code = item[airport_type]
                    airport_info = get_airport_coordinates(icao_code)
                    if airport_info:
                        name, latitude, longitude = airport_info
                        if latitude:
                            item[airport_type] = {
                                'ICAO': icao_code,
                                'name': name,
                                'latitude': latitude,
                                'longitude': longitude
                            }
                        else:
                            item[airport_type] = {
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