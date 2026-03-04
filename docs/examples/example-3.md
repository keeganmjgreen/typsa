# Quickstart 3 &ndash; Investments & Storage

*Adapted from: [PyPSA Quickstart 3 &ndash; Investments & Storage](https://docs.pypsa.org/latest/examples/example-3/)*


```python
import math
from typing import cast

import pandas as pd
import pypsa

import typsa
from typsa.components import (
    Bus,
    Carrier,
    ExtendableGenerator,
    ExtendableStorageUnit,
    Generator,
    Load,
)
from typsa.time_variation import TimestampedSeries
```

## Defining the Network


```python
def calculate_annuity(discount_rate: float, lifetime_years: int) -> float:
    return cast(float, pypsa.common.annuity(r=discount_rate, n=lifetime_years))
```


```python
demand_p_set = 100
solar_p_max_pu = TimestampedSeries(
    pd.read_csv(
        "https://model.energy/data/time-series-f17c3736a2719ce7da58484180d89e2d.csv",
        index_col="time",
        parse_dates=["time"],
    )["solar"]
)
inverter_capital_cost_per_mw = 170_000 * calculate_annuity(
    discount_rate=0.05, lifetime_years=25
)
storage_capital_cost_per_mw = 150_000 * calculate_annuity(
    discount_rate=0.05, lifetime_years=25
)
battery_energy_to_power_ratio = 4
battery_round_trip_efficiency = 0.9

network = typsa.Network(snapshots=solar_p_max_pu.snapshots)

network.add_components(
    ac_carrier := Carrier(name="AC"),
    grid_carrier := Carrier(name="grid_carrier"),
    solar_carrier := Carrier(name="solar_carrier"),
    battery_carrier := Carrier(name="battery_carrier"),
)
network.add_components(
    seville_bus := Bus(name="seville"),
    demand := Load(
        name="demand", bus=seville_bus.name, carrier=ac_carrier.name, p_set=demand_p_set
    ),
    grid := Generator(
        name="grid",
        bus=seville_bus.name,
        p_nom=demand_p_set,
        marginal_cost=120,
        carrier=grid_carrier.name,
    ),
    solar := ExtendableGenerator(
        name="solar",
        bus=seville_bus.name,
        p_max_pu=solar_p_max_pu,
        capital_cost=(
            400_000 * calculate_annuity(discount_rate=0.05, lifetime_years=25)
        ),
        carrier=solar_carrier.name,
    ),
    battery := ExtendableStorageUnit(
        name="battery",
        bus=seville_bus.name,
        capital_cost=(
            inverter_capital_cost_per_mw
            + battery_energy_to_power_ratio * storage_capital_cost_per_mw
        ),
        carrier=battery_carrier.name,
        efficiency_store=math.sqrt(battery_round_trip_efficiency),
        efficiency_dispatch=math.sqrt(battery_round_trip_efficiency),
        max_hours=battery_energy_to_power_ratio,
    ),
)
```

## Optimizing the Network


```python
optimized_network = network.model().optimize()
```


```python
optimized_network.static_results.all_capacities
```




    {'solar': PNomOpt(value=659.7784140420765),
     'battery': PNomOpt(value=351.37183897980725)}


