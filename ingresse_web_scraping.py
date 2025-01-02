from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback
# API META


def get_ticket_link_selenium(url):
    driver = webdriver.Chrome()
    driver.get(url)
    try:
        # Wait until url appears, you can adjust time
        link_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='tickets']"))
        )
        link = link_element.get_attribute("href")
    finally:
        driver.quit()
    return link
        

def get_jsons(url):
    api_url = url
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        #print(f"Erro: {response.status_code}")
        #print(response.text)
        pass
       
        
def clean_text(html_string):
    soup = BeautifulSoup(html_string, "html.parser")
    clean_text = soup.get_text(separator="\n")  # Uses \n to structure the text
    lines = clean_text.split("\n")
    filtered_lines = [
        line.strip() for line in lines
        if not line.startswith("http") and line.strip()  # Removes links and empty lines
    ]
    final_text = "\n".join(filtered_lines)
    return final_text
      
  
def extract_informations(url):
    data = get_jsons(url)
    
    event_dict = {}
    event_dict["name"] = data["title"]
    event_dict["description"] = clean_text(data["description"])
    event_dict["event_url"] = "https://ingresse.com/" + url.rsplit("/", 1)[-1]
    event_dict["products"] = {"buy_url": event_dict["event_url"]}
    # no artist
    # no tags 
    
    if data["poster"]:
        sizes = list(data["poster"].keys())[::-1]
        event_dict["img_url"] = data["poster"][sizes[0]]

    place = data["place"]
    if place:
        address = f"{place['street']}, {place['city']} - {place['state']}, {place['zip']}"
        zip_code = place["zip"]
        event_dict["address"] = {"address": address, "zip_code": zip_code}
        
    dates = data["sessions"]
    if dates:
        event_date = []
        for date in dates:
            event_date.append(date["dateTime"])
        if len(event_date) == 1:
            event_dict["start"] = event_date[0]
        else:
            event_dict["start"] = event_date

    return event_dict


if __name__ == "__main__":
    try:
        current_date = datetime.today()
        ufs = [
            "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
            "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
            "RS", "RO", "RR", "SC", "SP", "SE", "TO"
        ]
        
        # Get all event urls from Brazil
        event_links = []
        days_range = 30
        for uf in ufs:
            for day in range(days_range):
                iter_start_date = current_date + timedelta(days=day)
                iter_start_date = iter_start_date.strftime("%Y-%m-%d")
                iter_end_date = current_date + timedelta(days=day+2)
                iter_end_date = iter_end_date.strftime("%Y-%m-%d")
                iter_url = f"https://api-site.ingresse.com/events/search?company_id=1&iso_code=BRA-{uf}&date_from={iter_start_date}T00:00:00Z&date_to={iter_end_date}T00:00:00Z&size=40&offset=0&order_by_date=true"
                data = get_jsons(iter_url)
                if data:
                    for event in data["events"]:
                        slug = event["slug"]
                        event_links.append("https://api-site.ingresse.com/events/" + slug)    
                    total_pages = data["pagination"]["total_pages"]
                    if total_pages > 1:
                        for page in range(2, total_pages+1):
                            page_data = get_jsons(iter_url + "&page={page}")
                            for event in data["events"]:
                                slug = event["slug"]
                                event_links.append("https://api-site.ingresse.com/events/" + slug)
        event_links = list(set(event_links))
        
        # Get all event infos
        all_ingresse_events = []
        for url in event_links:
            event_dict = extract_informations(url)
            all_ingresse_events.append(event_dict)
            
            
    except Exception as e:
        error_message = traceback.format_exc()
        print("[ERRO] Ocorreu um problema ao executar o script.")
        print(error_message)
        
        # Envia alerta no WhatsApp
        #send_whatsapp_alert(f"Ocorreu um erro no script da EC2:\n\n{error_message}")
