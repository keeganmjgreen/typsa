# Quickstart 1 &ndash; Markets

*Adapted from: [PyPSA Quickstart 1 &ndash; Markets](https://docs.pypsa.org/latest/examples/example-1/)*


```python
import typsa
from typsa.components import Bus, Carrier, CustomLineParameters, Generator, Line, Load
```

## Defining the Network


```python
network = typsa.Network()

network.add_components(Carrier(name="AC"))
network.add_components(
    zone_1 := Bus(name="zone_1"),
    zone_2 := Bus(name="zone_2"),
)
network.add_components(
    Load(
        name="load_1",
        bus=zone_1.name,
        p_set=500,
    ),
    Load(
        name="load_2",
        bus=zone_2.name,
        p_set=1500,
    ),
)
network.add_components(
    Generator(
        name="gen_1",
        bus=zone_1.name,
        p_nom=2000,
        marginal_cost=10,
        marginal_cost_quadratic=0.005,
    ),
    Generator(
        name="gen_2",
        bus=zone_2.name,
        p_nom=2000,
        marginal_cost=13,
        marginal_cost_quadratic=0.01,
    ),
)
network.add_components(
    Line(
        name="line_1",
        bus0="zone_1",
        bus1="zone_2",
        parameters=CustomLineParameters(x=0.01),
        s_nom=400,
        carrier="AC",
    ),
)
```

## Optimizing the Network


```python
optimized_network = network.model().optimize()
```


```python
print(optimized_network.dynamic_results.of_all_generators.p)
```

    name      gen_1   gen_2
    snapshot               
    now       900.0  1100.0



```python
print(optimized_network.dynamic_results.of_all_buses.marginal_price)
```

    name        zone_1    zone_2
    snapshot                    
    now       19.00009  35.00011



```python
print(optimized_network.dynamic_results.of_all_lines.p1)
```

    name      line_1
    snapshot        
    now       -400.0

