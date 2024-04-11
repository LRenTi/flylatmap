import os
import json

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
        
        os.mkdir(export_folder)
        
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
        
        os.mkdir(import_folder)
        
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


def main():
    airport_table = Hashtable()
    icao = input("Enter ICAO code: ").upper()
    index = airport_table.hashfunction(icao)
    print(index)
    
if __name__ == "__main__":
    main()