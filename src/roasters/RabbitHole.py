from roasters.Roaster import Roaster
from bs4 import BeautifulSoup
import re

class RabbitHole(Roaster):
    def __init__(self):
        super().__init__(
            name="Rabbit Hole",
            main_url="https://www.rabbitholeroasters.com",
            product_url="/collections/all-coffee/products"
        )
    
    def get_coffee_information(self, soup:BeautifulSoup):
        name = soup.find("meta", {"property":"og:title", "content": True})["content"]
        price = soup.find("meta", {"property":"product:price:amount", "content": True})
        roast_lvl: str = ""
        
        if price:
            price = price["content"]
            
        desecription = soup.find("meta",  {"property":"og:description", "content": True})
        
        if desecription:
            roast_lvl = re.findall(r'\d+(?:\.\d+)?/\d+(?:\.\d+)?', desecription['content'])
            if roast_lvl:
                roast_lvl = roast_lvl[0]
            else:
                roast_lvl = "N/A"

        rte_div = soup.find('div', class_='Rte')
        impressions = ''
        process = ''
        country = ''

        if rte_div:
            # --- Impressions ---
            impressions_tag = rte_div.find(lambda tag: tag.name in ['strong', 'b'] and tag.get_text(strip=True) == 'Impressions:')
            if impressions_tag:
                for sibling in impressions_tag.next_siblings:
                    if isinstance(sibling, str):
                        text = sibling.strip()
                        if text:
                            impressions = text
                            break
                    elif hasattr(sibling, 'get_text'):
                        text = sibling.get_text(strip=True)
                        if text:
                            impressions = text
                            break

            # --- Process & Country ---
            for tag in rte_div.find_all(['p', 'div']):
                text = tag.get_text(separator='\n', strip=True)

                # Process
                if not process and 'Process:' in text:
                    for line in text.splitlines():
                        if 'Process:' in line:
                            process = line.split('Process:', 1)[1].strip()
                            break

                # Country
                if not country and 'Country:' in text:
                    for line in text.splitlines():
                        if 'Country:' in line:
                            country = line.split('Country:', 1)[1].strip()
                            break

                # Exit early if all found
                if process and country:
                    break
        
        if impressions:
            if not isinstance(impressions, str):
                impressions = ', '.join(impressions)

        return {"roaster": self.name, "name": name, "price": price, "roast_lvl": roast_lvl, "country":country, "process":process, "tasting_notes":impressions}