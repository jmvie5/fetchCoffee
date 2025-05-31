from roasters.Roaster import Roaster
from bs4 import BeautifulSoup
import re

class Cantook(Roaster):
    def __init__(self):
        super().__init__(
            name="Cantook",
            main_url="https://cantookcafe.com",
            product_url="/collections/cafes-de-specialite/products"
        )
    
    def get_coffee_information(self, soup:BeautifulSoup):
        name = soup.find("meta", {"property":"og:title", "content": True})["content"]
        price = soup.find("meta", {"property":"og:price:amount", "content": True})
        if price:
            price = price["content"]

        tasting_notes = "N/A"
        tasting_notes_div = soup.find('div', class_='product-single__box__text rte')
        if tasting_notes_div:
            for child in tasting_notes_div.find_all('h5', recursive=True):
                if not child.find('img') and child.get_text(strip=True):
                    tasting_notes = child.get_text(strip=True)

        rte_div = soup.find('div', class_='product-single__accordion__item-wrap rte')
        
        description_text = []
        for tag in rte_div.find_all(['h6', 'p', 'span']):
            text = tag.get_text(strip=True)
            description_text.append(text)

        roast_lvl = "N/A"
        process = "N/A"
        country = "N/A"
        for i, text in enumerate(description_text):
            if text.lower() == 'région':
                country = description_text[i + 1] if i + 1 < len(description_text) else "N/A"
            elif text.lower() == 'traitement':
                process = description_text[i + 1] if i + 1 < len(description_text) else "N/A"
                process.lower()
                process.replace("miel", "honey")
                process.replace("lavé", "washed")
                if process.lower().find("décaféiné") != -1:
                    process += " | decaffeinated"


        return {"roaster": self.name, "name": name, "price": price, "country":country, "roast_lvl": roast_lvl, "process":process, "tasting_notes": tasting_notes}