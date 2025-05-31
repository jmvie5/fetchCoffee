from roasters.RabbitHole import RabbitHole
from roasters.Detour import Detour
from roasters.Roaster import Roaster
from roasters.Cantook import Cantook
from roasters.FortyNine import FortyNine
import typer
from typing_extensions import Annotated
from datetime import datetime as Date, timedelta

roasters:dict[str, Roaster] = {
        'Rabbit_Hole': RabbitHole(),
        'Detour': Detour(),
        'Cantook': Cantook(),
        '49th': FortyNine()
    }

app = typer.Typer(no_args_is_help=True)

@app.command()
def ls(
    is_roaster: Annotated[bool, typer.Option(..., "--roaster", "-r", help="Possible roaster")] = False,
    is_country: Annotated[bool, typer.Option(..., "--country", "-c", help="Possible country or region of origin.")] = False,
    is_roast_lvl: Annotated[bool, typer.Option(..., "--roast", "-ro", help="Possible roast level.")] = False,
    is_tasting_notes: Annotated[bool, typer.Option(..., "--notes", "-n", help="Possible tasting notes.")] = False,
    is_process: Annotated[bool, typer.Option(..., "--process", "-pr", help="Possible processing method.")] = False,
    all: Annotated[bool, typer.Option(..., "--all", "-a", help="List all possible search term.")]=False
):
    """
    List possible search terms to use with fetch.
    """
    if not (is_roaster or is_country or is_roast_lvl or is_tasting_notes or is_process or all):
        typer.echo("Please specify at least one option to list possible search terms. Use --help for more information.")
        raise typer.Exit(code=1)
    if all:
        is_roaster = is_country = is_roast_lvl = is_tasting_notes = is_process = True
    
    if is_roaster:
        print("Available roasters:")
        for name in roasters.keys():
            print(f" - {name}")

    all_coffee_data = []
    for roaster in roasters:
        roasters[roaster].load_data_from_file()
        all_coffee_data.extend(roasters[roaster].coffee_data)


    fields = []
    if is_country:
        fields.append("country")
    if is_roast_lvl:
        fields.append("roast_lvl")
    if is_process:
        fields.append("process")
    if is_tasting_notes:
        fields.append("tasting_notes")

    keywords = get_all_coffee_data_keywords()

    for field in fields:
        print(f"\nPossible {field} keywords:")
        for kw in sorted(keywords[field]):
            print(f" - {kw}")
    

@app.command()
def fetch(
        roaster_filter: Annotated[list[str], typer.Option(..., "--roaster", "-r", help="Filter for roaster")] = [],
        max_price: Annotated[float, typer.Option(..., "--price", "-p", help="Set max price filter.")] = float('inf'),
        country: Annotated[str, typer.Option(..., "--country", "-c", help="Filter by country of origin.")] = "",
        process: Annotated[str, typer.Option(..., "--process", "-pr", help="Filter by processing method.")] = "",
        tasting_notes: Annotated[list[str], typer.Option(..., "--notes", "-n", help="Filter by tasting notes.")] = [],
        force_fetch: Annotated[bool, typer.Option(..., "--force", "-f", help="Force fetch new data even if not outdated.")] = False
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
                r.fetch_coffee_data(force_fetch)
                coffee_data.extend(r.coffee_data)
            else:
                print(f"Roaster '{roaster}' not found.")
                print("Available roasters:")
                for name in roasters.keys():
                    print(f" - {name}")
    else:
        for r in list(roasters.values()):
            r.fetch_coffee_data(force_fetch)
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
    print(f"Total coffees found: {len(coffee_data)}")
    

def format_coffee_data(coffee_data:list[dict]):
    res = ""
    for coffee in coffee_data:
        for data in coffee:
            res += f"   {data}: {coffee[data]}\n"
        res += f"\n"
    
    return res

def filter_coffee_data(coffee_data: list[dict], field: str, value) -> list[dict]:
    """
    Filter coffee data based on a field and value.
    
    Args:
        coffee_data: List of coffee dictionaries to filter
        field: The field to filter on (e.g. 'country', 'process')
        value: The value to filter for (can be string or list of strings)
        
    Returns:
        Filtered list of coffee dictionaries
    """
    filtered_coffees = []
    
    for coffee in coffee_data:
        field_value = coffee.get(field, '')
        
        # Skip if no value to check against
        if value is None:
            if not field_value:  # Keep items with empty field
                filtered_coffees.append(coffee)
            continue

        # Convert field value to string for searching
        if not isinstance(field_value, str):
            continue
            
        field_value = field_value.lower()

        if isinstance(value, str):
            if value.lower() in field_value:
                filtered_coffees.append(coffee)
                
        elif isinstance(value, list):
            for v in value:
                if v.lower() in field_value:
                    filtered_coffees.append(coffee)
                    break
                    
    return filtered_coffees

def get_all_coffee_data_keywords():
    all_coffee_data = []
    for roaster in roasters:
        roasters[roaster].load_data_from_file()
        all_coffee_data.extend(roasters[roaster].coffee_data)


    fields = ["country", "roast_lvl", "process", "tasting_notes"]
    keywords = {field: set() for field in fields}

    for coffee in all_coffee_data:
        for field in fields:
            value = coffee.get(field)
            if not value or value == "N/A":
                continue
            # Split tasting_notes and process by comma, others as is
            if field == "tasting_notes":
                for note in value.split(","):
                    note = note.strip().lower()
                    if note:
                        keywords[field].add(note)
            elif field == "process":
                for part in value.replace("+", ",").replace("&", ",").replace("/", ",").replace("|", ",").split(","):
                    part = part.strip().lower()
                    if part.find("decaf") != -1 or part.find("décaf") != -1:
                        part = "decaffeinated"
                    elif part.find("honey") != -1 or part.find("miel") != -1:
                        part = "honey"
                    elif part.find("washed") != -1 or part.find("lavé") != -1:
                        part = "washed"
                    elif part.find("natural") != -1 or part.find("naturel") != -1:
                        part = "natural"
                    if part:
                        keywords[field].add(part)
            elif field == "roast_lvl":
                for roast in value.replace("/", ",").replace("|", ",").replace(",", " ").split(" "):
                    roast = roast.strip().lower()
                    if roast == "roast":
                        continue
                    if roast:
                        keywords[field].add(roast)
            else:
                # Some fields may have slashes or pipes, split those too
                for part in value.replace("+", ",").replace("&", ",").replace("/", ",").replace("|", ",").split(","):
                    part = part.strip().lower()
                    if part.find("decaf") != -1 or part.find("décaf") != -1:
                        part = "decaffeinated"
                    elif part.find("honey") != -1 or part.find("miel") != -1:
                        part = "honey"
                    elif part.find("washed") != -1 or part.find("lavé") != -1:
                        part = "washed"
                    elif part.find("natural") != -1 or part.find("naturel") != -1:
                        part = "natural"
                    if part:
                        keywords[field].add(part)

    return keywords


if __name__ == "__main__":
    app()
