import csv
from datetime import datetime
from dateutil.parser import isoparse
from shotgun_web_scraping import *
from pixta_web_scraping import *

# Function to read existing events in the CSV file
def read_existing_events(filename='events.csv'):
    existing_events = set()
    try:
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                existing_events.add(row['name'])
    except FileNotFoundError:
        # If the file does not exist, we return an empty set
        pass
    return existing_events
    

# Function to remove expired events from CSV
def remove_expired_events(filename='events.csv'):
    try:
        # Read all CSV events
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            events = list(reader)  # Convert it into a list for manipulation
            
        # Filter only valid (non-expired) events
        valid_events = []
        for event in events:
            event_end_date = event.get('end', '')
            if event_end_date:
                try:
                    # Convert end date (ISO 8601) to datetime using dateutil.parser
                    event_end_datetime = isoparse(event_end_date)
                    #print(event.get("name", None), '|', event_end_date, '|', datetime.now(event_end_datetime.tzinfo), '|', event_end_datetime >= datetime.now(event_end_datetime.tzinfo))
                    if event_end_datetime >= datetime.now(event_end_datetime.tzinfo):  # Use date time zone
                        valid_events.append(event)
                except ValueError:
                    # If the date is invalid, keep the event in the file
                    valid_events.append(event)
        
        # Rewrite only valid events in CSV
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
            writer.writeheader()
            writer.writerows(valid_events)
    except FileNotFoundError:
        # If the file does not exist, nothing needs to be done
        pass


# Function to export data to a CSV file (without duplication)
def export_to_csv(data_list, filename='events.csv'):
    # Set CSV headers
    headers = [
        'event_url', 'name', 'start', 'end', 'address', 'description', 'tags', 'performers', 'products', 'img_url'
    ]
    
    # Get existing events in CSV to avoid duplication
    existing_events = read_existing_events(filename)
    
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        
        # Write headers only if file is empty
        if file.tell() == 0:
            writer.writeheader()
        
        # Iterate over each dictionary in the list
        for data in data_list:
            # Check if the event already exists in the CSV file
            event_name = data.get('name', '')
            if event_name in existing_events:
                continue  # Ignore duplications
            
            # Mark the event as added
            existing_events.add(event_name)
            
            # Write the line in CSV
            writer.writerow({
                'event_url': data.get('event_url', ''),
                'name': event_name,
                'start': data.get('start', ''),
                'end': data.get('end', ''),
                'address': data.get('address', ''),
                'description': data.get('description', ''),
                'tags': data.get('tags', ''),
                'performers': data.get('performers', ''),
                'products': data.get('products', ''),
                'img_url': data.get('img_url', ''),
            })
            
            
# Routine to create/update database of upcoming events
if __name__ == "__main__":
    export_to_csv(all_pixta_events)
    export_to_csv(all_shotgun_events)
    remove_expired_events()
