import requests
from bs4 import BeautifulSoup
import json
import traceback
# API META
        

# Function to get information from all events
def extract_informations(events_list):
    events_data = []
    for event in events_list:
        # Get general info
        event_dict = {}
        slug = event.get("slug", None)
        event_dict["name"] = event.get("name", None)
        event_dict["start"] = event.get("event_starts_at", None)
        event_dict["end"] = event.get("event_ends_at", None)
        tags = event.get("tag_list", None)
        event_dict["tags"] = event.get("tag_list", None)
        event_dict["img_url"] = event.get("cover_picture_url", None)
        event_dict["event_url"] = f"https://pixta.me/u/{slug}"
        products_list = []
        
        # Get address info
        address_dict = event.get("venue", None)
        if address_dict:
            street = address_dict.get("address_street", None)
            number = address_dict.get("address_number", None)
            city = address_dict.get("address_city", None)
            state = address_dict.get("address_state", None)
            zip_code = address_dict.get("address_zipcode", None)
            address = f"{street}, {number}, {city} - {state}, {zip_code}"
            event_dict["address"] = {"address": address, "zip_code": zip_code}
        
        # Get products info
        for product in event["products"]:
            product_dict = {}
            product_dict["product_name"] = product.get("name", None)
            product_dict["price"] = product.get("amount", None)
            product_dict["description"] = product.get("description", None)
            product_dict["price_currency"] = "BRL"
            product_slug = product.get("slug", None)
            product_dict["buy_url"] = event_dict["event_url"] + f"/{product_slug}"
            products_list.append(product_dict)
        event_dict["products"] = products_list
            
        # Get description
        event_resp = requests.get(event_dict["event_url"])
        if event_resp.status_code == 200:
            event_content = BeautifulSoup(event_resp.text, "html.parser")
            div_content = event_content.find("div", class_="px-2 my-4 prose dark:prose-invert prose-p:m-0")
            if div_content:
                description = div_content.get_text(strip=True, separator="\n")
                event_dict["description"] = description
            
        events_data.append(event_dict)
    return events_data


if __name__ == "__main__":
    try:
        # Get json from pixta
        resp = requests.get("https://api.pixta.me//api/health.json")
        content = BeautifulSoup(resp.text, "html.parser")
        dict_ = json.loads(content.text)
        events_list = dict_["events"]
        
        # Get all available cities
        cities_list = []
        for city in dict_["cities"]:
            if city["name"]:
                cities_list.append(city["slug"])
          
        # Get all events infos
        all_pixta_events = []
        for city in cities_list:
            resp = requests.get(f"https://api.pixta.me//api/cities/{city}.json?tag=")
            if resp.status_code != 200: continue
            conteudo = BeautifulSoup(resp.text, "html.parser")
            dict_ = json.loads(conteudo.text)
            events_list = dict_["events"]
            events_data = extract_informations(events_list)
            for event in events_data:
                all_pixta_events.append(event)
                
                
    except Exception as e:
        error_message = traceback.format_exc()
        print("[ERRO] Ocorreu um problema ao executar o script.")
        print(error_message)
        
        # Envia alerta no WhatsApp
        #send_whatsapp_alert(f"Ocorreu um erro no script da EC2:\n\n{error_message}")