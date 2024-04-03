from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import tqdm
import json

def extract_departure_destination(id):
    url = "https://flylat.net/company/routes/" + str(id)
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
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    driver.get(url)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
     
    data = {
        'name': airline_name,
        'id': id,
        'routes': [],
    }

    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        departure = ""
        destination = ""
        for row in rows:
            cells = row.find_all('td')
            if cells[0].text.strip() == 'Departure':
                departure = cells[1].text.strip()
            elif cells[0].text.strip() == 'Destination':
                destination = cells[1].text.strip()
                break 
        if departure and destination:
            data['routes'].append({"departure": departure, "destination": destination})
            
    print("loading...")
    save_url = 'Data/tmp_' + str(id) +'.json'
    with open(save_url, 'w') as f:
        json.dump(data, f)
        tqdm.tqdm.write("Data saved successfully.")

    driver.quit()

    return save_url