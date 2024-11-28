import csv
from datetime import datetime
from dateutil.parser import isoparse  # Importa o parser para datas ISO 8601
from shotgun_web_scraping import *
from pixta_web_scraping import *

# Função para ler os eventos existentes no arquivo CSV
def read_existing_events(filename='events.csv'):
    existing_events = set()
    try:
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                existing_events.add(row['name'])
    except FileNotFoundError:
        # Se o arquivo não existir, retornamos um set vazio
        pass
    return existing_events
    

# Função para remover eventos expirados do CSV
def remove_expired_events(filename='events.csv'):
    try:
        # Ler todos os eventos do CSV
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            events = list(reader)  # Convertemos em uma lista para manipulação
            
        # Filtrar apenas os eventos válidos (não expirados)
        valid_events = []
        for event in events:
            event_end_date = event.get('end', '')
            if event_end_date:
                try:
                    # Converter a data de término (ISO 8601) para datetime usando dateutil.parser
                    event_end_datetime = isoparse(event_end_date)
                    print(event.get("name", None), '|', event_end_date, '|', datetime.now(event_end_datetime.tzinfo), '|', event_end_datetime >= datetime.now(event_end_datetime.tzinfo))
                    if event_end_datetime >= datetime.now(event_end_datetime.tzinfo):  # Usa o fuso horário da data
                        valid_events.append(event)
                except ValueError:
                    # Se a data for inválida, manter o evento no arquivo
                    valid_events.append(event)
        
        # Regravar apenas os eventos válidos no CSV
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
            writer.writeheader()
            writer.writerows(valid_events)
    except FileNotFoundError:
        # Se o arquivo não existir, nada precisa ser feito
        pass


# Função para exportar os dados para um arquivo CSV (sem duplicação)
def export_to_csv(data_list, filename='events.csv'):
    # Definir os cabeçalhos do CSV
    headers = [
        'event_url', 'name', 'start', 'end', 'address', 'description', 'tags', 'performers', 'products', 'img_url'
    ]
    
    # Obter eventos já existentes no CSV para evitar duplicação
    existing_events = read_existing_events(filename)
    
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        
        # Escrever cabeçalhos apenas se o arquivo estiver vazio
        if file.tell() == 0:
            writer.writeheader()
        
        # Iterar sobre cada dicionário na lista
        for data in data_list:
            # Verificar se o evento já existe no arquivo CSV
            event_name = data.get('name', '')
            if event_name in existing_events:
                continue  # Ignorar duplicações
            
            # Marcar o evento como adicionado
            existing_events.add(event_name)
            
            # Escrever a linha no CSV
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
            
            
# Rotina para o banco de próximos eventos
export_to_csv(all_pixta_events)
export_to_csv(all_shotgun_events)
remove_expired_events()
