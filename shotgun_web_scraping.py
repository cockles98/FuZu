import requests
import json
from bs4 import BeautifulSoup
from dateutil.parser import isoparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import traceback
# API META


def extract_informations(scripts):
    "Function to get most event informations"
    event_dict = {}
    for script in scripts:
        try:
            data = json.loads(script.string)
            if all(key in data for key in ["name", "offers", "description", "performer"]):
                # get general info
                event_dict["name"] = data.get("name", None)
                #print(data.get("startDate", None), '|', isoparse(data.get("startDate", None)))
                event_dict["start"] = isoparse(data.get("startDate", None))
                event_dict["end"] = isoparse(data.get("endDate", None))
                event_dict["img_url"] = data.get("image", None)
                event_dict["event_url"] = data.get("url", None)
                performers = [artist['name'] for artist in data['performer']]
                event_dict["performers"] = ", ".join(performers)
                event_dict["description"] = data['description']
                
                # Get address info 
                address_dict = data.get("location", None).get("address", None)
                if address_dict:
                    address = address_dict.get("streetAddress", None)
                    zip_code = address_dict.get("postalCode", None)
                    event_dict["address"] = {"address": address, "zip_code": zip_code}
                
                # Get products info 
                products_list = []
                for product in data["offers"]:
                    product_dict = {}
                    product_dict["product_name"] = product.get("name", None)
                    product_dict["price"] = product.get("price", None)
                    product_dict["price_currency"] = product.get("priceCurrency", None)
                    product_dict["buy_url"] = event_dict["event_url"]
                    products_list.append(product_dict)
                event_dict["products"] = products_list

        except json.JSONDecodeError:
            continue
        
    return event_dict


def get_event_urls(city_url):
    # Config WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run without graphical interface
    options.add_argument('--disable-gpu')  # Optimization for systems without GPU support
    options.add_argument('--no-sandbox')  # For Linux environments

    # Start WebDriver
    driver = webdriver.Chrome(options=options)
    driver.get(city_url)

    # Click the "View More" button repeatedly until all content loads
    while True:
        try:
            # Wait until the button is visible and clickable
            wait = WebDriverWait(driver, 10)
            view_more_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "View more")]'))
            )
            # Click button
            view_more_button.click()
            time.sleep(2)
        except Exception:
            #print("Todos os dados foram carregados ou o botão não está mais disponível.")
            break

    # Get final HTML
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')

    # Close WebDriver
    driver.quit()

    # Get all event urls from current city
    event_urls = []
    for link in soup.find_all("a"):
        if "/en/events/" in str(link.get("href")):
            event_urls.append("https://shotgun.live/" + link.get("href"))

    return list(set(event_urls))
    

if __name__ == "__main__":
    try:
        # Get all available cities
        answer = requests.get("https://shotgun.live/en/cities")
        content = BeautifulSoup(answer.content, "html.parser")
        target_div = content.find("div", {"id": "br", "class": "relative space-y-8"})
        links = target_div.find_all("a", href=True)  # Search for links within the div
        cities_list = [
            link["href"].split("/")[-1]  # Extracts only "caxias-do-sul" from the link
            for link in links
            if "/en/cities/" in link["href"]  # Ensure it is a city link
        ]
           
        # Get all event urls
        all_event_urls = []
        for city in cities_list:
            city_url = f"https://shotgun.live/en/cities/{city}"
            event_urls = get_event_urls(city_url)
            for event in event_urls:  
                all_event_urls.append(event)
            
        # Get all event infos
        all_shotgun_events = []
        for url in all_event_urls:
            # Page connection
            answer = requests.get(url)
            content = BeautifulSoup(answer.text, "html.parser")
            
            # Get event info
            scripts = content.find_all('script', type='application/ld+json')
            event_dict = extract_informations(scripts)
            
            # Get event tags 
            div_tags = content.find("div", class_="flex flex-wrap gap-2")
            if div_tags:
                tags = []
                for tag in div_tags.find_all("a"):
                    tags.append(tag.text.strip())
                event_dict["tags"] = ", ".join(tag.capitalize() for tag in tags)
            
            # Save infos
            all_shotgun_events.append(event_dict)
        

    except Exception as e:
        error_message = traceback.format_exc()
        print("[ERRO] Ocorreu um problema ao executar o script.")
        print(error_message)
        
        # Envia alerta no WhatsApp
        #send_whatsapp_alert(f"Ocorreu um erro no script da EC2:\n\n{error_message}")