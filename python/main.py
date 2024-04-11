import database as db
import create_site as cs
import os
import json

def main():
    
    #id = 100172
    filename = "airports"
    airlinefile = "data/airlines.json"
    airport_table = db.Hashtable()
    airport_table.loadTable(filename)
    
    count_missing_airports = 0
    
    with open('data/airlines.json', 'r') as f:
        data = json.load(f)
        print(data)
    
    for airlines in data['airlines']:
        airline_id = airlines["id"]
        path = db.extract_departure_destination(airline_id)
        
        if path:
            count_missing_airports += db.get_Routes(path, airport_table)
            if os.path.exists(path):
                os.remove(path)
            #cs.create_site(airline_id)
            print("Data has been retrieved for airline ID:", airline_id)
        else:
            print("Data could not be retrieved for airline ID:", airline_id)
    
    airport_table.saveTable("airports")
    print("Missing airports:", count_missing_airports)

if __name__ == "__main__":
    main()