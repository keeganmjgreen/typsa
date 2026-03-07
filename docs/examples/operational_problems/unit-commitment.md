# Unit Commitment

*Adapted from: [PyPSA Examples &ndash; Unit Commitment](https://docs.pypsa.org/latest/examples/unit-commitment/)*


```python
import datetime as dt

import pandas as pd

import typsa
from typsa.components import (
    Bus,
    CommittableGenerator,
    ExtendableGenerator,
    Generator,
    Load,
)
from typsa.time_variation import IntegerSnapshots, RangedSeries
```


```python
def create_network(
    coal_plant: Generator | ExtendableGenerator,
    gas_plant: Generator | ExtendableGenerator,
    load: list[int],
) -> typsa.Network[IntegerSnapshots]:
    network = typsa.Network(
        IntegerSnapshots(range(len(load)), spacing=dt.timedelta(hours=1))
    )

    network.add_components(bus := Bus(name="bus"))
    network.add_components(coal_plant, gas_plant)
    network.add_components(
        Load(name="load", bus=bus.name, p_set=RangedSeries(pd.Series(load)))
    )
    return network


def report_results(
    optimized_network: typsa.network.OptimizedNetwork[IntegerSnapshots],
) -> None:
    dynamic_results = optimized_network.dynamic_results
    print(
        pd.concat(
            {
                "Generator dispatched power": dynamic_results.of_all_generators.p,
                "Committable generator status": dynamic_results.of_committable_generators.status.astype(
                    bool
                ),
            },
            axis="columns",
        )
    )
```

## Minimum Part Load


```python
optimized_network, _ = create_network(
    CommittableGenerator(
        name="coal",
        bus="bus",
        p_min_pu=0.3,
        marginal_cost=20,
        p_nom=10_000,
    ),
    CommittableGenerator(
        name="gas",
        bus="bus",
        p_min_pu=0.1,
        marginal_cost=70,
        p_nom=1_000,
    ),
    load=[4_000, 6_000, 5_000, 800],
).optimize()
```


```python
report_results(optimized_network)
```

             Generator dispatched power        Committable generator status       
    name                           coal    gas                         coal    gas
    snapshot                                                                      
    0                            4000.0    0.0                         True  False
    1                            6000.0    0.0                         True  False
    2                            5000.0    0.0                         True  False
    3                               0.0  800.0                        False   True


## Minimum Up Time


```python
optimized_network, _ = create_network(
    CommittableGenerator(
        name="coal",
        bus="bus",
        p_min_pu=0.3,
        marginal_cost=20,
        p_nom=10_000,
    ),
    CommittableGenerator(
        name="gas",
        bus="bus",
        p_min_pu=0.1,
        marginal_cost=70,
        p_nom=1_000,
        up_time_before=0,
        min_up_time=3,
    ),
    load=[4_000, 800, 5_000, 3_000],
).optimize()
```


```python
report_results(optimized_network)
```

             Generator dispatched power        Committable generator status       
    name                           coal    gas                         coal    gas
    snapshot                                                                      
    0                            3900.0  100.0                         True   True
    1                               0.0  800.0                        False   True
    2                            4900.0  100.0                         True   True
    3                            3000.0   -0.0                         True  False


## Minimum Down Time


```python
optimized_network, _ = create_network(
    CommittableGenerator(
        name="coal",
        bus="bus",
        p_min_pu=0.3,
        marginal_cost=20,
        p_nom=10_000,
        min_down_time=2,
        down_time_before=1,
    ),
    CommittableGenerator(
        name="gas",
        bus="bus",
        p_min_pu=0.1,
        marginal_cost=70,
        p_nom=4_000,
    ),
    load=[3_000, 800, 3_000, 8_000],
).optimize()
```


```python
report_results(optimized_network)
```

             Generator dispatched power         Committable generator status  \
    name                           coal     gas                         coal   
    snapshot                                                                   
    0                               0.0  3000.0                        False   
    1                               0.0   800.0                        False   
    2                            3000.0     0.0                         True   
    3                            8000.0     0.0                         True   
    
                     
    name        gas  
    snapshot         
    0          True  
    1          True  
    2         False  
    3         False  


## Start Up and Shut Down Costs


```python
optimized_network, _ = create_network(
    CommittableGenerator(
        name="coal",
        bus="bus",
        p_min_pu=0.3,
        marginal_cost=20,
        p_nom=10_000,
        start_up_cost=5_000,
        min_down_time=2,
    ),
    CommittableGenerator(
        name="gas",
        bus="bus",
        p_min_pu=0.1,
        marginal_cost=70,
        p_nom=4_000,
        shut_down_cost=25,
    ),
    load=[3_000, 800, 3_000, 8_000],
).optimize()
```


```python
report_results(optimized_network)
```

             Generator dispatched power         Committable generator status  \
    name                           coal     gas                         coal   
    snapshot                                                                   
    0                               0.0  3000.0                        False   
    1                               0.0   800.0                        False   
    2                            3000.0     0.0                         True   
    3                            8000.0     0.0                         True   
    
                     
    name        gas  
    snapshot         
    0          True  
    1          True  
    2         False  
    3         False  


## Ramp Rate Limits


```python
optimized_network, _ = create_network(
    Generator(
        name="coal",
        bus="bus",
        marginal_cost=20,
        ramp_limit_up=0.1,
        ramp_limit_down=0.2,
        p_nom=10_000,
    ),
    Generator(
        name="gas",
        bus="bus",
        marginal_cost=70,
        p_nom=4_000,
    ),
    load=[4_000, 7_000, 7_000, 7_000, 7_000, 3_000],
).optimize()
```


```python
report_results(optimized_network)
```

             Generator dispatched power        
    name                           coal     gas
    snapshot                                   
    0                            4000.0    -0.0
    1                            5000.0  2000.0
    2                            6000.0  1000.0
    3                            7000.0    -0.0
    4                            5000.0  2000.0
    5                            3000.0    -0.0



```python
optimized_network, _ = create_network(
    extendable_coal_plant := ExtendableGenerator(
        name="coal",
        bus="bus",
        marginal_cost=20,
        ramp_limit_up=0.1,
        ramp_limit_down=0.2,
        capital_cost=100,
    ),
    Generator(
        name="gas",
        bus="bus",
        marginal_cost=70,
        p_nom=4_000,
    ),
    load=[4_000, 7_000, 7_000, 7_000, 7_000, 3_000],
).optimize()
```


```python
optimized_network.static_results.capacity_of(extendable_coal_plant)
```




    PNomOpt(value=5000.0)




```python
report_results(optimized_network)
```

             Generator dispatched power        
    name                           coal     gas
    snapshot                                   
    0                            4000.0    -0.0
    1                            4500.0  2500.0
    2                            5000.0  2000.0
    3                            5000.0  2000.0
    4                            4000.0  3000.0
    5                            3000.0    -0.0



```python
optimized_network, _ = create_network(
    CommittableGenerator(
        name="coal",
        bus="bus",
        p_min_pu=0.05,
        ramp_limit_up=0.2,
        ramp_limit_down=0.25,
        p_nom=10_000,
        ramp_limit_start_up=0.1,
        ramp_limit_shut_down=0.15,
    ),
    Generator(
        name="gas",
        bus="bus",
        marginal_cost=70,
        p_nom=10_000,
    ),
    load=[0, 200, 7_000, 7_000, 7_000, 2_000, 0],
).optimize()
```


```python
report_results(optimized_network)
```

             Generator dispatched power         Committable generator status
    name                           coal     gas                         coal
    snapshot                                                                
    0                               0.0     0.0                        False
    1                               0.0   200.0                        False
    2                            1000.0  6000.0                         True
    3                            3000.0  4000.0                         True
    4                            4000.0  3000.0                         True
    5                            1500.0   500.0                         True
    6                               0.0     0.0                        False


## Rolling Horizon


```python
load = [4_000, 5_000, 700, 800, 4_000] * 6
optimized_network, _ = create_network(
    CommittableGenerator(
        name="coal",
        bus="bus",
        p_min_pu=0.3,
        marginal_cost=20,
        ramp_limit_up=1,
        ramp_limit_down=1,
        p_nom=10_000,
        start_up_cost=200,
        shut_down_cost=150,
        min_up_time=3,
        min_down_time=2,
        up_time_before=1,
        ramp_limit_start_up=1,
        ramp_limit_shut_down=1,
    ),
    CommittableGenerator(
        name="gas",
        bus="bus",
        marginal_cost=70,
        p_min_pu=0.1,
        p_nom=1_000,
        start_up_cost=50,
        shut_down_cost=20,
        min_up_time=3,
        up_time_before=2,
    ),
    load=load,
).optimize(horizon=5, overlap=2)
```


```python
print(
    pd.concat(
        {
            "Generator dispatched power": optimized_network.dynamic_results.of_all_generators.p,
            "Committable generator status": optimized_network.dynamic_results.of_committable_generators.status.astype(
                bool
            ),
        },
        axis="columns",
    )
)
```

             Generator dispatched power        Committable generator status       
    name                           coal    gas                         coal    gas
    snapshot                                                                      
    0                            3900.0  100.0                         True   True
    1                            4900.0  100.0                         True   True
    2                               0.0  700.0                        False   True
    3                               0.0  800.0                        False   True
    4                            4000.0    0.0                         True  False
    5                            4000.0    0.0                         True  False
    6                            5000.0    0.0                         True  False
    7                               0.0  700.0                        False   True
    8                               0.0  800.0                        False   True
    9                            3900.0  100.0                         True   True
    10                           4000.0    0.0                         True  False
    11                           4900.0  100.0                         True   True
    12                              0.0  700.0                        False   True
    13                              0.0  800.0                        False   True
    14                           4000.0    0.0                         True  False
    15                           4000.0    0.0                         True  False
    16                           4900.0  100.0                         True   True
    17                              0.0  700.0                        False   True
    18                              0.0  800.0                        False   True
    19                           4000.0    0.0                         True  False
    20                           4000.0    0.0                         True  False
    21                           4900.0  100.0                         True   True
    22                              0.0  700.0                        False   True
    23                              0.0  800.0                        False   True
    24                           4000.0    0.0                         True  False
    25                           4000.0    0.0                         True  False
    26                           5000.0    0.0                         True  False
    27                              0.0  700.0                        False   True
    28                              0.0  800.0                        False   True
    29                           3900.0  100.0                         True   True

