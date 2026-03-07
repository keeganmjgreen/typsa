# Electricity Markets

*Adapted from: [PyPSA Examples &ndash; Electricity Markets](https://docs.pypsa.org/latest/examples/simple-electricity-market-examples/)*

PyPSA seeks to minimize the total cost of a network. Because this includes operational costs of electricity market resources such as generators, PyPSA can be used to model electricity markets and clear them. When an electricity market is cleared, it determines which generators to schedule/dispatch as well as the market-clearing price(s).

This example shows how to use TyPSA to model increasingly complex electricity markets.


```python
import datetime as dt
from typing import Literal

import pandas as pd

import typsa
from typsa.components import Bus, Carrier, Generator, Link, Load, StorageUnit
from typsa.time_variation import IntegerSnapshots, RangedSeries, Static
```


```python
type Tech = Literal["Wind", "Hydro", "Coal", "Gas", "Oil"]
type Country = Literal["South Africa", "Mozambique", "Eswatini"]

MARGINAL_COST_LOOKUP: dict[Tech, float] = {
    "Wind": 0,
    "Hydro": 0,
    "Coal": 30,
    "Gas": 60,
    "Oil": 80,
}
POWER_PLANT_P_NOM_LOOKUP: dict[Country, dict[Tech, float]] = {
    "South Africa": {"Coal": 35000, "Wind": 3000, "Gas": 8000, "Oil": 2000},
    "Mozambique": {"Hydro": 1200},
    "Eswatini": {"Hydro": 600},
}
TRANSMISSION_LOOKUP: dict[tuple[Country, Country], float] = {
    ("South Africa", "Mozambique"): 500,
    ("South Africa", "Eswatini"): 250,
    ("Mozambique", "Eswatini"): 100,
}
LOAD_LOOKUP: dict[Country, float] = {
    "South Africa": 42000,
    "Mozambique": 650,
    "Eswatini": 250,
}
```


```python
def create_network(countries: list[Country]) -> typsa.Network:
    network = typsa.Network()
    network.add_components(Carrier(name="AC"))
    for country in countries:
        network.add_components(Bus(name=country))
        for tech in POWER_PLANT_P_NOM_LOOKUP[country]:
            network.add_components(
                Generator(
                    name=f"{country} {tech}",
                    bus=country,
                    p_nom=POWER_PLANT_P_NOM_LOOKUP[country][tech],
                    marginal_cost=MARGINAL_COST_LOOKUP[tech],
                )
            )
        network.add_components(
            Load(name=f"{country} load", bus=country, p_set=LOAD_LOOKUP[country])
        )
    for (country, other_country), p_nom in TRANSMISSION_LOOKUP.items():
        if country in countries and other_country in countries:
            network.add_components(
                Link(
                    name=f"{country} - {other_country} link",
                    bus0=country,
                    bus1=other_country,
                    p_nom=p_nom,
                    p_min_pu=-1,
                )
            )
    return network


def report_results(
    optimized_network: (
        typsa.network.OptimizedNetwork[Static]
        | typsa.network.OptimizedNetwork[IntegerSnapshots]
    ),
) -> None:
    print("Generator dispatched power:\n")
    print(optimized_network.dynamic_results.of_all_generators.p.T)
    print()
    print("Zone marginal price:\n")
    print(optimized_network.dynamic_results.of_all_buses.marginal_price.T)
    if len(optimized_network.links) > 0:
        print()
        print("Transmission:\n")
        link_dynamic_results = optimized_network.dynamic_results.of_all_links
        print(
            pd.concat(
                {
                    "power": link_dynamic_results.p0.T,
                    "shadow price": link_dynamic_results.mu_lower.T,
                },
                axis="columns",
            ).reorder_levels([1, 0], axis="columns")
        )
    if len(optimized_network.storage_units) > 0:
        print()
        print("Storage unit:\n")
        storage_unit_dynamic_results = (
            optimized_network.dynamic_results.of_all_storage_units
        )
        print(
            pd.concat(
                {
                    "dispatched power": storage_unit_dynamic_results.p,
                    "state of charge": storage_unit_dynamic_results.state_of_charge,
                },
                axis="columns",
            ).reorder_levels([1, 0], axis="columns")
        )
```

## Single bidding zone with fixed load, one period


```python
optimized_sa_network, _ = create_network(countries=["South Africa"]).optimize()
```


```python
report_results(optimized_sa_network)
```

    Generator dispatched power:
    
    snapshot               now
    name                      
    South Africa Coal  35000.0
    South Africa Wind   3000.0
    South Africa Gas    4000.0
    South Africa Oil      -0.0
    
    Zone marginal price:
    
    snapshot       now
    name              
    South Africa  60.0


## Three bidding zones connected by transmission, one period


```python
optimized_three_country_network, _ = create_network(
    countries=["South Africa", "Mozambique", "Eswatini"]
).optimize()
```


```python
report_results(optimized_three_country_network)
```

    Generator dispatched power:
    
    snapshot               now
    name                      
    South Africa Coal  35000.0
    South Africa Wind   3000.0
    South Africa Gas    3250.0
    South Africa Oil      -0.0
    Mozambique Hydro    1050.0
    Eswatini Hydro       600.0
    
    Zone marginal price:
    
    snapshot       now
    name              
    South Africa  60.0
    Mozambique    -0.0
    Eswatini      -0.0
    
    Transmission:
    
    snapshot                          now             
                                    power shadow price
    name                                              
    South Africa - Mozambique link -500.0          NaN
    South Africa - Eswatini link   -250.0          NaN
    Mozambique - Eswatini link     -100.0          NaN


## Single bidding zone with price-sensitive industrial load, one period


```python
sa_network = create_network(countries=[country := "South Africa"])
sa_network.add_components(
    Generator(
        name=f"{country} industrial load",
        bus=country,
        p_max_pu=0,
        p_min_pu=-1,
        p_nom=8000,
        marginal_cost=70,
    )
)
optimized_sa_network, _ = sa_network.optimize()
```


```python
report_results(optimized_sa_network)
```

    Generator dispatched power:
    
    snapshot                          now
    name                                 
    South Africa Coal             35000.0
    South Africa Wind              3000.0
    South Africa Gas               8000.0
    South Africa Oil                 -0.0
    South Africa industrial load  -4000.0
    
    Zone marginal price:
    
    snapshot       now
    name              
    South Africa  70.0


## Single bidding zone with fixed load, several periods


```python
country: Country = "South Africa"

sa_network = typsa.Network(IntegerSnapshots(range(4), spacing=dt.timedelta(hours=1)))
sa_network.add_components(Carrier(name="AC"))
sa_network.add_components(Bus(name=country))
for tech in POWER_PLANT_P_NOM_LOOKUP[country]:
    sa_network.add_components(
        Generator(
            name=f"{country} {tech}",
            bus=country,
            p_nom=POWER_PLANT_P_NOM_LOOKUP[country][tech],
            marginal_cost=MARGINAL_COST_LOOKUP[tech],
            p_max_pu=(
                RangedSeries(pd.Series([0.3, 0.6, 0.4, 0.5])) if tech == "Wind" else 1
            ),
        )
    )
sa_network.add_components(
    Load(
        name=f"{country} load",
        bus=country,
        p_set=RangedSeries(LOAD_LOOKUP[country] + pd.Series([0, 1000, 3000, 4000])),
    )
)

optimized_sa_network, _ = sa_network.optimize()
```


```python
report_results(optimized_sa_network)
```

    Generator dispatched power:
    
    snapshot                 0        1        2        3
    name                                                 
    South Africa Coal  35000.0  35000.0  35000.0  35000.0
    South Africa Wind    900.0   1800.0   1200.0   1500.0
    South Africa Gas    6100.0   6200.0   8000.0   8000.0
    South Africa Oil      -0.0     -0.0    800.0   1500.0
    
    Zone marginal price:
    
    snapshot         0     1     2     3
    name                                
    South Africa  60.0  60.0  80.0  80.0


## Single bidding zone with fixed load and storage, several periods


```python
sa_network.add_components(
    StorageUnit(
        name=f"{country} pumped hydro",
        bus=country,
        p_nom=1000,
        max_hours=6,
    )
)
optimized_sa_network, _ = sa_network.optimize()
```


```python
report_results(optimized_sa_network)
```

    Generator dispatched power:
    
    snapshot                 0        1        2        3
    name                                                 
    South Africa Coal  35000.0  35000.0  35000.0  35000.0
    South Africa Wind    900.0   1800.0   1200.0   1500.0
    South Africa Gas    6900.0   7200.0   8000.0   8000.0
    South Africa Oil      -0.0     -0.0     -0.0    500.0
    
    Zone marginal price:
    
    snapshot         0     1     2     3
    name                                
    South Africa  60.0  60.0  60.0  80.0
    
    Storage unit:
    
    name     South Africa pumped hydro                
                      dispatched power state of charge
    snapshot                                          
    0                           -800.0           800.0
    1                          -1000.0          1800.0
    2                            800.0          1000.0
    3                           1000.0            -0.0

