import requests
from bs4 import BeautifulSoup
import simplejson as json
from datetime import datetime as Date, timedelta

class Roaster:

    def __init__(self, name:str, main_url:str, product_url:str):
        self.name = name
        self.main_url = main_url
        self.product_url = product_url
        self.data_timestamp = '1970-01-01'
        self.coffee_data = []

    def __str__(self):
        res = f"""
        - {self.name} -\n\n"""
        for coffee in self.coffee_data:
            for data in coffee:
                res += f"   {data}: {coffee[data]}\n"
            res += f"\n"
        
        return res

    def load_data_from_file(self, path:str = "data/data.json"):
        try:
            with open(path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if self.name in data['roasters']:
                    self.coffee_data = data['roasters'][self.name]['coffee_data']
                    self.data_timestamp = data['roasters'][self.name]['timestamp']
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"roasters": {}}


    def save_data_to_file(self, path:str = "data/data.json"):
        try:
            with open(path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"roasters": {}}

        # Update the data
        data['roasters'][self.name] = {
            "timestamp": Date.now().strftime("%Y-%m-%d"),
            "coffee_data": self.coffee_data
        }

        # Overwrite the file safely
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
            print(f"Saved data for {self.name} to file.")

    def fetch_coffee_data(self, force_fetch:bool = False):
        self.load_data_from_file()
        now = Date.now().date()
        if (force_fetch or Date.strptime(self.data_timestamp, "%Y-%m-%d").date() + timedelta(weeks=1) < now):
            print(f"Outdated or no data. Fetching new data for {self.name}...")
            self.data_timestamp = now
            url = self.main_url + self.product_url
            main_soup = self.generate_soup(url)
            self.coffee_data = self.extract_coffee_data_from_soup(main_soup)
            self.save_data_to_file()
            

    # UTILS

    def generate_soup(self, url):
        response = requests.get(url)
        return BeautifulSoup(response.text, "html.parser")

    def get_links_deeper_than(self, soup:BeautifulSoup, product_url:str):
        links = []
        for link in soup.find_all("a"):
            href = link.get("href")
            if href:
                # Only add links that are deeper than the product_url
                if href != product_url and href.startswith(product_url):
                    links.append(href)
        return links

    def get_coffee_information(self, soup:BeautifulSoup):
        pass


    def extract_coffee_data_from_soup(self, soup:BeautifulSoup):
        coffee_data =[]
        coffee_pages = self.get_links_deeper_than(soup, self.product_url)
        coffee_data = []
        visited_pages = set()
        for coffee in coffee_pages:
            if coffee not in visited_pages:
                visited_pages.add(coffee)
                coffee_soup = self.generate_soup(self.main_url + coffee)
                coffee_info = self.get_coffee_information(coffee_soup)
                coffee_info["url"] = self.main_url + coffee
                coffee_data.append(coffee_info)
                print(f"\rFetched data for {len(coffee_data)} coffees.", end="")
        print("") # New line after the progress update
        return coffee_data
