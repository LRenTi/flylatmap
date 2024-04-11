import requests
import json
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from tqdm import tqdm
from dotenv import load_dotenv

def mkdir(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

class Airport:
    def __init__(self, icao, name, latitude, longitude):
        self.icao = icao
        self.name = name
        self.latitude = latitude
        self.longitude = longitude

class Hashtable:
    def __init__(self):
        self.size = 78007  # 60000 Airports * 30% + 7 for prime number
        self.table = [None] * self.size

    def hashfunction(self, key):
        hashValue = 0
        primeNumber = 79
        for char in key:
            hashValue = (hashValue * primeNumber + ord(char))
        return hashValue % self.size
    
    def addAirport(self, airport):
        index = 0
        index = self.hashfunction(airport.icao)
        
        if self.table[index] is None:
            self.table[index] = airport
        else:
            print("Collision detected for", airport.icao)
            
    def saveTable(self, fileName):
        data = []
        export_folder = "data/"
        
        mkdir(export_folder)
        
        file_path = export_folder + fileName + ".json"
        
        airport_data = {}
        
        for index in range(self.size):
            if self.table[index] is not None:
                airport_data = {
                    "Index": index,
                    "ICAO": self.table[index].icao,
                    "Name": self.table[index].name,
                    "Latitude": self.table[index].latitude,
                    "Longitude": self.table[index].longitude
                }
                data.append(airport_data)

        with open(file_path, 'w') as file:
            json.dump(data, file)

        print("Hashtable data saved to", file_path)
        
    def loadTable(self, fileName):
        import_folder = "data/"
        
        mkdir(import_folder)
        
        file_path = import_folder + fileName + ".json"
        
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                for item in data:
                    index = item["Index"]  # Convert "Index" to an integer
                    icao = item["ICAO"]
                    name = item["Name"]
                    latitude = item["Latitude"]
                    longitude = item["Longitude"]
                    
                    self.table[index] = Airport(icao, name, latitude, longitude)
                    
                print("Hashtable data loaded from", file_path)
        except FileNotFoundError:
            print("The specified file was not found:", file_path)
        except json.JSONDecodeError:
            print("Error decoding the JSON file:", file_path)

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
def get_Routes(path, table):
    with open(path, 'r') as f:
        data = json.load(f)
        
        departure_destination_list = data['routes']
        
        newdata = {
            'name': data['name'],
            'id': data['id'],
            'updateTimestamp': time.time(),
            'routes': [],
        }
        
        index = 0
        count_missing_airports = 0
                
        for item in tqdm(departure_destination_list):
            for airport in ['departure', 'destination']:
                if airport in item:
                    icao_code = item[airport]
                    index = table.hashfunction(icao_code)
                    if table.table[index] is not None:
                        airport_info = table.table[index].name, table.table[index].latitude, table.table[index].longitude
                    else:
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
                            count_missing_airports += 1
                        if table.table[index] is None:
                            table.addAirport(Airport(icao_code, name, latitude, longitude))
                    else:
                        print(f"\nCould not retrieve data for {icao_code}")
        newdata['routes'] = departure_destination_list
        
        folder = 'data/routes/'
        mkdir(folder)
        newpath = folder + str(data['id']) + '.json'
        
        with open(newpath, 'w') as f:
            json.dump(newdata, f)
        
        return count_missing_airports
def extract_departure_destination(id):
    url = "https://flylat.net/company/get_routes.php?id=" + str(id)
    name_url = "https://flylat.net/company/" + str(id)
    
    name_response = requests.get(name_url)

    if name_response.status_code == 200:
        soup = BeautifulSoup(name_response.text, 'html.parser')

        airline_name_tag = soup.find('td', text='Airline Name').find_next_sibling('td')
        if airline_name_tag:
            airline_name = airline_name_tag.text.strip()
        else:
            airline_name = None
    print(airline_name)
     
    data = {
        'name': airline_name,
        'id': id,
        'routes': [],
    }
    
    response = requests.get(url)
    
    if response.status_code == 200:
        routes = response.json()

        for route in tqdm(routes):
            departure = route['dep']
            destination = route['des']
            data['routes'].append({"departure": departure, "destination": destination})
            
    save_url = 'Data/tmp_' + str(id) +'.json'
    with open(save_url, 'w') as f:
        json.dump(data, f)
        tqdm.write("Extracted data saved successfully.")


    return save_url