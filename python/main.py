import database as db
import create_site as cs
import os

def main():
    
    #id = 100172
    filename = "airports"
    airlinefile = "data/airlines.json"
    airport_table = db.Hashtable()
    airport_table.loadTable(filename)
    
    # Iterate over all airline IDs in the JSON
    for airline_id in airlinefile:
        path = db.extract_departure_destination(airline_id)
        
        if path:
            db.get_Routes(path, airport_table)
            if os.path.exists(path):
                os.remove(path)
            #cs.create_site(airline_id)
        else:
            print("Data could not be retrieved for airline ID:", airline_id)
    
    
    print("You find the airline ID in the URL: e.g. https://flylat.net/company/100172")
    id = input("Enter the airline ID: ")
    print("Please wait, the data is being retrieved from flylat.net")
    
    
    path = db.extract_departure_destination(id)
    
    if path:
        db.get_Routes(path, airport_table)
        if os.path.exists(path):
            os.remove(path)
        #cs.create_site(id)
    else:
        print("Data could not be retrieved from flylat.net")
        
    

    airport_table.saveTable("airports")

if __name__ == "__main__":
    main()