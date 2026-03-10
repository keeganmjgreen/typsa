# Quickstart 2 &ndash; Power Flow

*Adapted from: [PyPSA Quickstart 2 &ndash; Power Flow](https://docs.pypsa.org/latest/examples/example-2/)*


```python
import typsa
from typsa.components import Bus, Carrier, CustomLineParameters, Generator, Line, Load
```

## Defining the Network


```python
network = typsa.Network()

v_nom = 11
network.add_components(Carrier(name="AC"))
network.add_components(
    zone_1 := Bus(name="zone_1", v_nom=v_nom),
    zone_2 := Bus(name="zone_2", v_nom=v_nom),
    zone_3 := Bus(name="zone_3", v_nom=v_nom),
)
network.add_components(
    Load(name="load_1", bus=zone_1.name, p_set=50),
    Load(name="load_2", bus=zone_2.name, p_set=60),
    Load(name="load_3", bus=zone_3.name, p_set=300),
)
network.add_components(
    Generator(name="gen_a", bus=zone_1.name, p_nom=140, marginal_cost=7.5),
    Generator(name="gen_b", bus=zone_1.name, p_nom=285, marginal_cost=6),
    Generator(name="gen_c", bus=zone_2.name, p_nom=90, marginal_cost=14),
    Generator(name="gen_d", bus=zone_3.name, p_nom=85, marginal_cost=10),
)
network.add_components(
    Line(
        name="line_1",
        bus0=zone_1.name,
        bus1=zone_2.name,
        s_nom=126,
        parameters=CustomLineParameters(x=0.02, r=0.01),
    ),
    Line(
        name="line_2",
        bus0=zone_1.name,
        bus1=zone_3.name,
        s_nom=250,
        parameters=CustomLineParameters(x=0.02, r=0.01),
    ),
    Line(
        name="line_3",
        bus0=zone_2.name,
        bus1=zone_3.name,
        s_nom=130,
        parameters=CustomLineParameters(x=0.01, r=0.01),
    ),
)
```

## Optimizing the Network


```python
optimized_network, _ = network.optimize()
```


```python
print(optimized_network.dynamic_results.of_all_buses.marginal_price)
```

    name      zone_1  zone_2  zone_3
    snapshot                        
    now          7.5   11.25    10.0



```python
print(optimized_network.dynamic_results.of_all_generators.p)
```

    name      gen_a  gen_b  gen_c  gen_d
    snapshot                            
    now        50.0  285.0   -0.0   75.0



```python
print(optimized_network.dynamic_results.of_all_lines.p0)
```

    name      line_1  line_2  line_3
    snapshot                        
    now        126.0   159.0    66.0


## Simulating the Network (Power Flow)


```python
pf_results = optimized_network.pf()
```


```python
print(pf_results.of_all_generators.p)
```

    name          gen_a  gen_b  gen_c  gen_d
    snapshot                                
    now       53.860705  285.0   -0.0   75.0



```python
print(pf_results.of_all_generators.q)
```

    name         gen_a  gen_b  gen_c  gen_d
    snapshot                               
    now       7.379326    0.0    0.0    0.0



```python
print(pf_results.of_all_lines.q0)
```

    name        line_1    line_2    line_3
    snapshot                              
    now      -1.811567  9.190894 -4.388279

