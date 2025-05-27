from roasters.RabbitHole import RabbitHole
from roasters.Detour import Detour
from roasters.Roaster import Roaster
import typer
from typing_extensions import Annotated

roasters:dict[str, Roaster] = {
        'Rabbit Hole': RabbitHole(),
        'Detour': Detour()
    }

app = typer.Typer(no_args_is_help=True)

@app.command()
def ls():
    """
    List all available roasters.
    """
    print("Available roasters:")
    for name in roasters.keys():
        print(f" - {name}")

@app.command()
def fetch(
        roaster_filter: Annotated[list[str], typer.Option(..., "--roaster", "-r", help="Filter for roaster")] = [],
        max_price: Annotated[float, typer.Option(..., "--price", "-p", help="Set max price filter.")] = float('inf'),
        country: Annotated[str, typer.Option(..., "--country", "-c", help="Filter by country of origin.")] = "",
        process: Annotated[str, typer.Option(..., "--process", "-pr", help="Filter by processing method.")] = "",
        tasting_notes: Annotated[str, typer.Option(..., "--notes", "-n", help="Filter by tasting notes.")] = ""
):
    """
    Fetch coffee data from the specified roaster or all roasters if none is specified.
    """

    if (max_price != float('inf')):
        print(f"Max price {max_price}.")
        return
    
    coffee_data = []

    if (roaster_filter):
        print(f"Filtering for roasters: {', '.join(roaster_filter)}")
        for roaster in roaster_filter:
            if roaster in roasters:
                r = roasters[roaster]
                r.load_data_from_file()
                coffee_data.extend(r.coffee_data)
            else:
                print(f"Roaster '{roaster}' not found.")
                print("Available roasters:")
                for name in roasters.keys():
                    print(f" - {name}")
    else:
        for r in list(roasters.values()):
            r.fetch_coffee_data()
            coffee_data.extend(r.coffee_data)

    if country:
        coffee_data = filter_coffee_data(coffee_data, 'country', country)
        print(f"Filtered by country: {country}")
    if process:
        coffee_data = filter_coffee_data(coffee_data, 'process', process)
        print(f"Filtered by process: {process}")
    if tasting_notes:
        coffee_data = filter_coffee_data(coffee_data, 'tasting_notes', tasting_notes)
        print(f"Filtered by tasting notes: {tasting_notes}")

    if len(coffee_data) == 0:
        print("No coffee data found with the specified filters.")
        return
    
    print(format_coffee_data(coffee_data))
    

def format_coffee_data(coffee_data:list[dict]):
    res = ""
    for coffee in coffee_data:
        for data in coffee:
            res += f"   {data}: {coffee[data]}\n"
        res += f"\n"
    
    return res

def filter_coffee_data(coffee_data, field: str, value):
    return [
        coffee for coffee in coffee_data
        if (
            (value is None and not coffee.get(field)) or
            (isinstance(value, str) and isinstance(coffee.get(field), str) and value.lower() in coffee.get(field, '').lower())
        )
    ]

if __name__ == "__main__":
    app()
