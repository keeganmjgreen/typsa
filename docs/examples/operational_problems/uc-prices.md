# Negative Prices in Linearized Unit Commitment

*Adapted from: [PyPSA Examples &ndash; Negative Prices in Linearized Unit Commitment](https://docs.pypsa.org/latest/examples/uc-prices/)*


```python
import datetime as dt

import pandas as pd

import typsa
from typsa.components import Bus, Carrier, CommittableGenerator, Load
from typsa.time_variation import IntegerSnapshots, RangedSeries
```


```python
network = typsa.Network(IntegerSnapshots(range(5), spacing=dt.timedelta(hours=1)))

network.add_components(Carrier(name="AC"))
network.add_components(bus := Bus(name="bus", carrier="AC"))
network.add_components(
    load := Load(
        name="load",
        bus=bus.name,
        p_set=RangedSeries(pd.Series([50, 120, 50, 20, 50])),
    )
)
base_generator_marginal_cost = 20
network.add_components(
    base_generator := CommittableGenerator(
        name="base",
        bus=bus.name,
        p_nom=100,
        marginal_cost=base_generator_marginal_cost,
        p_min_pu=0.4,
        start_up_cost=4000,
        shut_down_cost=2000,
    ),
    peak_generator := CommittableGenerator(
        name="peak",
        bus=bus.name,
        p_nom=50,
        marginal_cost=70,
        p_min_pu=0.2,
        start_up_cost=250,
    ),
)
```


```python
optimized_network, _ = network.optimize(linearized_unit_commitment=True)
```


```python
dispatch = optimized_network.dynamic_results.of_all_generators.p
status = optimized_network.dynamic_results.of_committable_generators.status
pd.DataFrame(
    {
        "Load (MW)": optimized_network.dynamic_results.of_all_loads.p[load.name],
        "Base Gen (MW)": dispatch[base_generator.name],
        "Peak Gen (MW)": dispatch[peak_generator.name],
        "Total Gen (MW)": dispatch.sum(axis="columns"),
        "Base Status": status[base_generator.name],
        "Peak Status": status[peak_generator.name],
        "Price (€/MWh)": optimized_network.dynamic_results.of_all_buses.marginal_price[
            bus.name
        ],
    }
).rename_axis("Time Period")
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Load (MW)</th>
      <th>Base Gen (MW)</th>
      <th>Peak Gen (MW)</th>
      <th>Total Gen (MW)</th>
      <th>Base Status</th>
      <th>Peak Status</th>
      <th>Price (€/MWh)</th>
    </tr>
    <tr>
      <th>Time Period</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>50.0</td>
      <td>50.0</td>
      <td>-0.0</td>
      <td>50.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>20.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>120.0</td>
      <td>100.0</td>
      <td>20.0</td>
      <td>120.0</td>
      <td>1.0</td>
      <td>0.4</td>
      <td>75.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>50.0</td>
      <td>50.0</td>
      <td>-0.0</td>
      <td>50.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>20.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>20.0</td>
      <td>20.0</td>
      <td>-0.0</td>
      <td>20.0</td>
      <td>0.5</td>
      <td>0.0</td>
      <td>-30.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>50.0</td>
      <td>50.0</td>
      <td>-0.0</td>
      <td>50.0</td>
      <td>0.5</td>
      <td>0.0</td>
      <td>20.0</td>
    </tr>
  </tbody>
</table>
</div>




```python
periods_low = [2, 3, 4]

cycle_cost = base_generator.start_up_cost + base_generator.shut_down_cost

gen_low = float(dispatch.loc[periods_low, base_generator.name].sum())
op_cost = gen_low * base_generator_marginal_cost

print("Why stay online?")
print("=" * 25)
print(f"Start-up cost:        {base_generator.start_up_cost:,.0f} €")
print(f"Shut-down cost:       {base_generator.shut_down_cost:,.0f} €")
print(f"Total cycling cost:   {cycle_cost:,.0f} €\n")

print(f"Output (snapshots 2-4): {gen_low:.1f} MWh")
print(f"Operational cost:       {op_cost:,.0f} €\n")

decision = "Stay online" if op_cost < cycle_cost else "Cycle off/on"
savings = abs(cycle_cost - op_cost)

print(f"Decision: {decision} is cheaper.")
print(f"Savings vs alternative: {savings:,.0f} €")
```

    Why stay online?
    =========================
    Start-up cost:        4,000 €
    Shut-down cost:       2,000 €
    Total cycling cost:   6,000 €
    
    Output (snapshots 2-4): 120.0 MWh
    Operational cost:       2,400 €
    
    Decision: Stay online is cheaper.
    Savings vs alternative: 3,600 €

