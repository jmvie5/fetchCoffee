from roasters.RabbitHole import RabbitHole
from roasters.Detour import Detour
from roasters.Roaster import Roaster
import typer
from typing_extensions import Annotated


app = typer.Typer(no_args_is_help=True)


@app.command()
def fetch(
        roaster: Annotated[str, typer.Argument(..., help="Name of the roaster to list coffee data for. If not provided, lists all roasters.")] = "",
        max_price: Annotated[float, typer.Option(..., "--price", "-p", help="Set max price filter.")] = float('inf'),
        country: Annotated[str, typer.Option(..., "--country", "-c", help="Filter by country of origin.")] = "",
        process: Annotated[str, typer.Option(..., "--process", "-pr", help="Filter by processing method.")] = "",
):
    roasters:dict[str, Roaster] = {
        'Rabbit Hole': RabbitHole(),
        'Detour': Detour()
    }

    if (max_price != float('inf')):
        print(f"Max price {max_price}.")
        return
    
    coffee_data = []

    if (roaster):
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

    print(format_coffee_data(coffee_data))
    

def format_coffee_data(coffee_data:list[dict]):
        res = ""
        for coffee in coffee_data:
            for data in coffee:
                res += f"   {data}: {coffee[data]}\n"
            res += f"\n"
        
        return res


if __name__ == "__main__":
    app()
