from bs4 import BeautifulSoup
import requests
import re

rabbit_hole_main_url = "https://www.rabbitholeroasters.com"
rabbit_hole_product_url = "/collections/all-coffee/products"
response = requests.get(rabbit_hole_main_url + rabbit_hole_product_url)
soup = BeautifulSoup(response.text, "html.parser")

def generate_soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, "html.parser")

def get_links_deeper_than(soup:BeautifulSoup, url:str):
    links = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if href:
            # Only add links that are deeper than the initial page
            if href != url and href.startswith(url):
                links.append(href)
    return links

def get_coffee_information(soup:BeautifulSoup):
    
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
    return {"name": name, "price": price, "roast_lvl": roast_lvl}


# Extract all links deeper then the initial page
coffee_pages = get_links_deeper_than(soup, rabbit_hole_product_url)
coffee_data = []
for coffee in coffee_pages:
    coffee_soup = generate_soup(rabbit_hole_main_url + coffee)
    coffee_info = get_coffee_information(coffee_soup)
    coffee_info["url"] = rabbit_hole_main_url + coffee
    coffee_data.append(coffee_info)

# Print the coffee data
for coffee in coffee_data:
    print(f"Name: {coffee['name']}, Price: {coffee['price']}, Roast Level: {coffee['roast_lvl']}, URL: {coffee['url']}")

# Print the coffee data with price bellow 25
# for coffee in coffee_data:
#     if float(coffee["price"]) < 25:
#         print(f"Name: {coffee['name']}, Price: {coffee['price']}, Roast Level: {coffee['roast_lvl']}, URL: {coffee['url']}")

# Print the coffee data with price above 25
# for coffee in coffee_data:
#     if float(coffee["price"]) > 25:
#         print(f"Name: {coffee['name']}, Price: {coffee['price']}, Roast Level: {coffee['roast_lvl']}, URL: {coffee['url']}")
