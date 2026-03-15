# Meshed AC-DC Networks

*Adapted from: [PyPSA Examples &ndash; Meshed AC-DC Networks](https://docs.pypsa.org/latest/examples/ac-dc-lopf/)*


```python
import pandas as pd
import pypsa

import typsa
from typsa.time_variation import TimestampSnapshots
```


```python
pypsa_network = pypsa.examples.ac_dc_meshed()
pypsa_network.links.at["Norwich Converter", "p_nom_extendable"] = False
network = typsa.Network.from_pypsa_network(pypsa_network, TimestampSnapshots)
```

    INFO:pypsa.network.io:Retrieving network data from https://github.com/PyPSA/PyPSA/raw/v1.0.7/examples/networks/ac-dc-meshed/ac-dc-meshed.nc.
    INFO:pypsa.network.io:New version 1.1.2 available! (Current: 1.0.7)
    INFO:pypsa.network.io:Imported network 'AC-DC-Meshed' has buses, carriers, generators, global_constraints, lines, links, loads



```python
topology_determined_network = network.determine_network_topology()
sub_networks_df = pd.DataFrame(
    map(dict, topology_determined_network.sub_networks)
).set_index("name", drop=False)
sub_networks_df["n_branches"] = sub_networks_df.index.map(
    {k: len(v) for k, v in topology_determined_network.branches_by_sub_network.items()}
)
sub_networks_df["n_buses"] = sub_networks_df.index.map(
    {k: len(v) for k, v in topology_determined_network.buses_by_sub_network.items()}
)
print(sub_networks_df)
```

    WARNING:pypsa.networks:The network has not been optimized yet and no model is stored.


         name carrier   slack_bus  n_branches  n_buses
    name                                              
    0       0      AC  Manchester         3.0        3
    1       1      DC  Norwich DC         3.0        3
    2       2      AC   Frankfurt         1.0        2
    3       3      AC      Norway         NaN        1



```python
optimized_network, optimization_info = network.optimize()
```


```python
print(f"{optimization_info.objective_value = }")
```

    optimization_info.objective_value = -3474094.130816232



```python
if optimization_info.objective_value is not None:
    print(
        f"{optimization_info.objective_value + optimization_info.objective_constant = }"
    )
```

    optimization_info.objective_value + optimization_info.objective_constant = 18440973.38746291



```python
{
    g: optimized_network.static_results.all_capacities[g]
    for g in optimized_network.generators
}
```




    {'Manchester Wind': PNomOpt(value=4090.809778349753),
     'Manchester Gas': PNomOpt(value=-0.0),
     'Norway Wind': PNomOpt(value=1533.5998578542462),
     'Norway Gas': PNomOpt(value=-0.0),
     'Frankfurt Wind': PNomOpt(value=1667.7244197394368),
     'Frankfurt Gas': PNomOpt(value=982.0344827209511)}




```python
print(optimized_network.dynamic_results.of_all_generators.p)
```

    name                 Manchester Wind  Manchester Gas  Norway Wind  Norway Gas  \
    snapshot                                                                        
    2015-01-01 00:00:00       739.970940            -0.0  1494.620662        -0.0   
    2015-01-01 01:00:00      1987.100952            -0.0   738.106855        -0.0   
    2015-01-01 02:00:00       858.392169            -0.0   624.521432        -0.0   
    2015-01-01 03:00:00       807.813368            -0.0   920.106182        -0.0   
    2015-01-01 04:00:00       452.526516            -0.0   804.324386        -0.0   
    2015-01-01 05:00:00      2469.206273            -0.0    14.864732        -0.0   
    2015-01-01 06:00:00      2770.854059            -0.0   338.087245        -0.0   
    2015-01-01 07:00:00      1478.020255            -0.0  1263.561295        -0.0   
    2015-01-01 08:00:00      2520.688233            -0.0   853.033829        -0.0   
    2015-01-01 09:00:00      2133.432454            -0.0   673.888373        -0.0   
    
    name                 Frankfurt Wind  Frankfurt Gas  
    snapshot                                            
    2015-01-01 00:00:00      932.388707      -0.000000  
    2015-01-01 01:00:00     1255.647012      -0.000000  
    2015-01-01 02:00:00      205.905743      -0.000000  
    2015-01-01 03:00:00     1612.150259      -0.000000  
    2015-01-01 04:00:00     1432.588292      -0.000000  
    2015-01-01 05:00:00      877.479528     982.034483  
    2015-01-01 06:00:00      129.904072      -0.000000  
    2015-01-01 07:00:00       98.434885      -0.000000  
    2015-01-01 08:00:00      414.520401      -0.000000  
    2015-01-01 09:00:00      180.214589     483.239904  



```python
optimized_network.dynamic_results.of_all_buses.marginal_price.mean(axis=1)
```




    snapshot
    2015-01-01 00:00:00       0.110000
    2015-01-01 01:00:00    1421.808212
    2015-01-01 02:00:00       0.110000
    2015-01-01 03:00:00       0.110000
    2015-01-01 04:00:00       0.110000
    2015-01-01 05:00:00    1593.642751
    2015-01-01 06:00:00       0.637904
    2015-01-01 07:00:00    1006.924472
    2015-01-01 08:00:00       0.269581
    2015-01-01 09:00:00    1490.788021
    dtype: float64




```python
print(optimized_network.dynamic_results.of_all_links.p0.round(2))
```

    name                 Norwich Converter  Norway Converter  Bremen Converter  \
    snapshot                                                                     
    2015-01-01 00:00:00            -250.84            674.58           -423.74   
    2015-01-01 01:00:00             315.07           -116.73           -198.34   
    2015-01-01 02:00:00             350.76            581.97           -932.73   
    2015-01-01 03:00:00             -85.77            272.56           -186.79   
    2015-01-01 04:00:00             317.37            -79.75           -237.62   
    2015-01-01 05:00:00             386.75           -494.20            107.45   
    2015-01-01 06:00:00             900.00           -257.52           -642.48   
    2015-01-01 07:00:00             123.68            971.92          -1095.60   
    2015-01-01 08:00:00             244.72            850.88          -1095.60   
    2015-01-01 09:00:00             820.02            -86.85           -733.17   
    
    name                 DC link  
    snapshot                      
    2015-01-01 00:00:00  -318.00  
    2015-01-01 01:00:00  -318.00  
    2015-01-01 02:00:00  -318.00  
    2015-01-01 03:00:00  -318.00  
    2015-01-01 04:00:00  -318.00  
    2015-01-01 05:00:00  -318.00  
    2015-01-01 06:00:00   318.00  
    2015-01-01 07:00:00   -86.86  
    2015-01-01 08:00:00   318.00  
    2015-01-01 09:00:00   -83.68  



```python
print(optimized_network.dynamic_results.of_all_lines.p0.round(2))
```

    name                      0        1       2       3       4       5        6
    snapshot                                                                     
    2015-01-01 00:00:00   79.47   -38.11  -52.97 -303.81  370.78 -202.73  -534.34
    2015-01-01 01:00:00 -449.46   787.04 -211.27  103.80  -12.93  209.36  -823.21
    2015-01-01 02:00:00 -181.27   520.56 -505.91 -155.15  426.82 -248.68   173.90
    2015-01-01 03:00:00  -45.47   234.47  -34.04 -119.81  152.75 -232.72  -743.79
    2015-01-01 04:00:00  -73.21   295.42 -227.20   90.17   10.42 -240.11  -883.82
    2015-01-01 05:00:00 -594.50  1198.08 -125.90  260.84 -233.35   19.36 -1030.85
    2015-01-01 06:00:00 -661.29  1378.42 -632.37  267.63   10.11  -53.45   319.39
    2015-01-01 07:00:00 -383.77   540.91 -469.93 -346.25  625.67  393.72   600.73
    2015-01-01 08:00:00 -778.28  1444.07 -522.12 -277.40  573.48  229.29   501.35
    2015-01-01 09:00:00 -465.58   899.57 -632.37  187.65  100.80   78.62  -248.57



```python
print(optimized_network.dynamic_results.of_all_buses.p.round(2))
```

    name                  London  Norwich  Norwich DC  Manchester   Bremen  \
    snapshot                                                                 
    2015-01-01 00:00:00   282.20  -164.62     -250.84     -117.58  -534.34   
    2015-01-01 01:00:00  -658.83  -577.67      315.07     1236.50  -823.21   
    2015-01-01 02:00:00    67.41  -769.24      350.76      701.83   173.90   
    2015-01-01 03:00:00   187.24  -467.19      -85.77      279.94  -743.79   
    2015-01-01 04:00:00   166.90  -535.53      317.37      368.63  -883.82   
    2015-01-01 05:00:00  -613.86 -1178.72      386.75     1792.58 -1030.85   
    2015-01-01 06:00:00  -607.85 -1431.87      900.00     2039.72   319.39   
    2015-01-01 07:00:00  -777.48  -147.19      123.68      924.68   600.73   
    2015-01-01 08:00:00 -1007.58 -1214.77      244.72     2222.35   501.35   
    2015-01-01 09:00:00  -544.19  -820.95      820.02     1365.14  -248.57   
    
    name                 Bremen DC  Frankfurt  Norway  Norway DC  
    snapshot                                                      
    2015-01-01 00:00:00    -423.74     534.34     0.0     674.58  
    2015-01-01 01:00:00    -198.34     823.21    -0.0    -116.73  
    2015-01-01 02:00:00    -932.73    -173.90     0.0     581.97  
    2015-01-01 03:00:00    -186.79     743.79     0.0     272.56  
    2015-01-01 04:00:00    -237.62     883.82     0.0     -79.75  
    2015-01-01 05:00:00     107.45    1030.85     0.0    -494.20  
    2015-01-01 06:00:00    -642.48    -319.39     0.0    -257.52  
    2015-01-01 07:00:00   -1095.60    -600.73     0.0     971.92  
    2015-01-01 08:00:00   -1095.60    -501.35     0.0     850.88  
    2015-01-01 09:00:00    -733.17     248.57     0.0     -86.85  

