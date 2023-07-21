import requests
from dotenv import dotenv_values
from bs4 import BeautifulSoup
import jsonlines
import json


class WebScraper:

    config = dotenv_values(".env")
    PROXY = config['PROXY'].split(':')
    PORT = PROXY[2]
    PASSWORD_ADRESS=PROXY[1].split('@')
    next_site_exists = True
    proxies = {
        "http" : f"http://{PROXY[0]}:{PASSWORD_ADRESS[0]}@{PASSWORD_ADRESS[1]}:{PORT}",
        "https" : f"https://{PROXY[0]}:{PASSWORD_ADRESS[0]}@{PASSWORD_ADRESS[1]}:{PORT}"
    }

    def generate_json(file_path: str, data_list: list):
        with jsonlines.open(file_path, 'w') as json:
            for element in data_list:    
                json.write(element)


    def data_parsing(quotes_json: list):
        for i in quotes_json:
            data_dict = {
                "text" : i['text'],
                "by" : i['author']['name'],
                "tags" : i['tags']
            }
        return data_dict


    def website_scraper(self):
        itr = 1
        data_dict_list=[]
        while self.next_site_exists:

            url = f"{self.config['INPUT_URL']}page/{str(itr)}"

            try:
                response = requests.get(url, timeout=1000, proxies=self.proxies)
                response.raise_for_status()
            except requests.exceptions.RequestException as exc:
                print(f"An error occured while making the request: {exc}")
                break

            soup = BeautifulSoup(response.content, 'html.parser')
            scripts = soup.find_all("script")
            next_site = soup.findAll('li', {"class": "next"})

            for script in scripts:
                if 'var data' in script.text:
                    quotes_data = script.text.split('var data =')[-1].strip()[:-1]
                    break

            start_index = quotes_data.find('[')
            end_index = quotes_data.find('];')
            quotes_json = quotes_data[start_index:end_index + 1]
            
            try:
                quotes_json = json.loads(quotes_json)
            except json.JSONDecodeError as exc:
                print(f"Error decoding json data: {exc}")
                break

            for i in quotes_json:
                data_dict = {
                    "text" : i['text'],
                    "by" : i['author']['name'],
                    "tags" : i['tags']
                }
                data_dict_list.append(data_dict)

            if not next_site:

                self.next_site_exists = False
                break

            itr+=1

        return data_dict_list


ws = WebScraper()
quotes_data = ws.website_scraper()
WebScraper.generate_json(WebScraper.config['OUTPUT_FILE'], quotes_data)

