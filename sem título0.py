import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
from dateutil.parser import isoparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.chrome.service import Service
#from webdriver_manager.chrome import ChromeDriverManager
        

ufs = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
    "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
    "RS", "RO", "RR", "SC", "SP", "SE", "TO"
]
ingresse_base_html = "https://www.ingresse.com/"
current_date = datetime.today()


for uf in ufs:
    for day in range(61):
        iter_start_date = current_date + timedelta(days=day)
        iter_start_date = iter_start_date.strftime("%Y-%m-%d")
        iter_end_date = current_date + timedelta(days=day+2)
        iter_end_date = iter_end_date.strftime("%Y-%m-%d")
        print(iter_start_date, iter_end_date)
        for page in range(1,3):
            iter_resp = requests.get(f"https://www.ingresse.com/search/?location={uf}&start_date={iter_start_date}T00%3A00%3A00Z&end_date={iter_end_date}T00:00:00Z&language=pt_br&page={page}")
            content = BeautifulSoup(iter_resp.text, "html.parser")
            pass




# Get json from pixta
resp = requests.get("https://www.ingresse.com/search/?location=BRA-RJ&start_date=2025-01-03T00:00:00Z&end_date=2025-01-05T00:00:00Z&language=pt_br")
content = BeautifulSoup(resp.text, "html.parser")
divs = content.find_all("div", style="opacity: 0; transform: translateY(50px) translateZ(0px);")
links = []
for div in divs:
        a_tag = div.find("a", href=True)
        if a_tag:
            links.append(a_tag["href"])
            
print(divs)
# Exibir os links coletados
print("Links coletados:")
for link in links:
    print(link)
    
    
###############################################################################
    
    
    
    
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run without graphical interface
options.add_argument('--disable-gpu')  # Optimization for systems without GPU support
options.add_argument('--no-sandbox')  # For Linux environments
    
# Start WebDriver
driver = webdriver.Chrome(options=options)
driver.get("https://www.ingresse.com/search/?location=BRA-RJ&start_date=2025-01-03T00:00:00Z&end_date=2025-01-05T00:00:00Z&language=pt_br")

# Rolar para o final antes de esperar pelo elemento
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(2)  # Aguarde o carregamento

# Get final HTML
html_content = driver.page_source
soup = BeautifulSoup(html_content, 'html.parser')

# Get links
divs = soup.find_all("div", style="opacity: 1; transform: none;")
links = []
for div in divs:
        a_tag = div.find("a", href=True)
        if a_tag:
            links.append(a_tag["href"])

# Close WebDriver
driver.quit()








from mitmproxy import http
from datetime import datetime
import json

class Interceptor:
    def __init__(self):
        # Arquivo onde os logs serão salvos
        self.log_file = open("requests_log.json", "w", encoding="utf-8")

    def request(self, flow: http.HTTPFlow):
        """
        Método chamado para cada requisição feita pela página.
        """
        request = flow.request
        data = {
            "timestamp": str(datetime.now()),
            "method": request.method,
            "url": request.pretty_url,
            "headers": dict(request.headers),
            "body": request.text if request.body else None
        }
        print(f"Interceptado: {data['url']}")  # Mostra a URL no console
        self.log_file.write(json.dumps(data, ensure_ascii=False) + "\n")

    def done(self):
        """
        Método chamado quando o mitmdump finaliza.
        """
        self.log_file.close()


addons = [
    Interceptor()  # Adiciona a classe de interceptação
]
