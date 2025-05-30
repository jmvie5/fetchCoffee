from roasters.Roaster import Roaster
from bs4 import BeautifulSoup

class FortyNine(Roaster):
    def __init__(self):
        super().__init__(
            name="49th",
            main_url="https://49thcoffee.com",
            product_url="/collections/all/products/"
        )
    
    def get_coffee_information(self, soup:BeautifulSoup):
        name = soup.find("meta", {"property":"og:title", "content": True})["content"]
        price_tags = soup.findAll("span", class_='money', recursive=True)
        for tag in price_tags:
            if tag.get_text(strip=True):
                price = tag.get_text(strip=True)
                price.replace(" ", "")
                if price.startswith("$"):
                    price = price[1:]
                break
 
        tasting_notes = []
        tasting_notes_elements = soup.findAll('span', class_='productitem--profile', recursive=True)
        if tasting_notes_elements:
            for note in tasting_notes_elements:
                if note.get_text(strip=True):
                    tasting_notes.append(note.get_text(strip=True))
        if ((len(tasting_notes) == 0)):
            tasting_notes = "N/A"
        else:
            tasting_notes = ', '.join(tasting_notes)

        rte_div = soup.find('div', class_='product-details__wrapper')
        
        description_text = []
        if rte_div:
            for tag in rte_div.find_all('li'):
                text = tag.get_text(strip=True)
                description_text.append(text)

        roast_lvl = "N/A"
        process = "N/A"
        country = "N/A"
        for i, text in enumerate(description_text):
            content = str(text).lower().split(':')
            if content[0].find('country') != -1:
                country = content[1] if len(content) > 1 else "N/A"
            if content[0].find('process') != -1:
                process = content[1] if len(content) > 1 else "N/A"
                process.lower()
                process.replace("miel", "honey")
                process.replace("lavé", "washed")
            if content[0].find('roast') != -1:
                roast_lvl = content[1] if len(content) > 1 else "N/A"


        return {"roaster": self.name, "name": name, "price": price, "country":country, "roast_lvl": roast_lvl, "process":process, "tasting_notes": tasting_notes}