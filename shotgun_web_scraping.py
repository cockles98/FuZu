import requests
import json
from bs4 import BeautifulSoup
from dateutil.parser import isoparse


# Function to get most event informations
def extract_informations(scripts):
    event_dict = {}
    for script in scripts:
        try:
            data = json.loads(script.string)
            if all(key in data for key in ["name", "offers", "description", "performer"]):
                # get general info
                event_dict["name"] = data.get("name", None)
                print(data.get("startDate", None), '|', isoparse(data.get("startDate", None)))
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


# Get all event pages
event_urls = []
answer = requests.get("https://shotgun.live/en/events")
content = BeautifulSoup(answer.text, "html.parser")
if answer.status_code != 200: 
    print("Fail in load the initial event page.")
for link in content.find_all("a"):
    if "/en/events/" in str(link.get("href")):
        event_urls.append(link.get("href"))

for i in range(2,100):
    answer = requests.get(f"https://shotgun.live/en/events/-/{i}")
    content = BeautifulSoup(answer.text, "html.parser")
    if answer.status_code != 200: 
        break
    for link in content.find_all("a"):
        if "/en/events/" in str(link.get("href")):
            event_urls.append(link.get("href"))


# Get all events infos
all_shotgun_events = []
for url in event_urls:
    # Page connection
    answer = requests.get("https://shotgun.live" + url)
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