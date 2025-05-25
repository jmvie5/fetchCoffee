from roasters.RabbitHole import RabbitHole
from roasters.Detour import Detour
from Roaster import Roaster


roasters = [
    RabbitHole(),
    Detour()
]


def fetch_all_coffee_data(roasters: list[Roaster]):
    for roaster in roasters:
        roaster.fetch_coffee_data()
        print(roaster)

fetch_all_coffee_data(roasters)
