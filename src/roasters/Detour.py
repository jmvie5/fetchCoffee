from roasters.Roaster import Roaster
from bs4 import BeautifulSoup
import re

class Detour(Roaster):
    def __init__(self):
        super().__init__(
            name="Detour Coffee Roasters",
            main_url="https://detourcoffee.com",
            product_url="/collections/direct-trade-coffee/products"
        )
    
    def get_coffee_information(self, soup:BeautifulSoup):
        name = soup.find("meta", {"property":"og:title", "content": True})["content"]
        price = soup.find("meta", {"property":"og:price:amount", "content": True})
        if price:
            price = price["content"]

        # Find the outer tasting-profile div
        profile_div = soup.find('div', class_='tasting-profile')
        tasting_notes = []
        if profile_div:
            # Get all inner divs that contain text but not <img>
            for child in profile_div.find_all('div', recursive=True):
                if not child.find('img') and child.get_text(strip=True):
                    tasting_notes.append(child.get_text(strip=True))
        tasting_notes = ', '.join(tasting_notes) if tasting_notes else "N/A"
        
        roast_lvl = ""
        desecription = soup.find("meta",  {"property":"og:description", "content": True})
        
        if desecription:
            roast_lvl = re.findall(r'\d+(?:\.\d+)?/\d+(?:\.\d+)?', desecription['content'])
            if roast_lvl:
                roast_lvl = roast_lvl[0]
            else:
                roast_lvl = "N/A"

        # Process
        info_div = soup.find('div', class_='info-table')

        process_value = None

        if info_div:
            rows = info_div.find_all('tr')
            for row in rows:
                columns = row.find_all('td')
                if len(columns) == 2 and columns[0].get_text(strip=True) == 'Process':
                    process_value = columns[1].get_text(strip=True)
                    break


        return {"roaster": "Detour", "name": name, "price": price, "roast_lvl": roast_lvl, "process":process_value, "tasting_notes": tasting_notes}