import extract_data as ed
import create_database as cd
import os

def main():
    
    id = 100172

    path = ed.extract_departure_destination(id)

    if path:
        cd.get_Routes(path)
        if os.path.exists(path):
            os.remove(path)
    else:
        print("Data could not be retrieved from flylat.net")

if __name__ == "__main__":
    main()