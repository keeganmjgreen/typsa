# SciGRID Network

*Adapted from: [PyPSA Examples – SciGRID Network](https://docs.pypsa.org/latest/examples/scigrid-lopf-then-pf/)*


```python
import datetime as dt
from typing import cast

import numpy as np
import pandas as pd
import pypsa

import typsa
from typsa.components.generator import Generator
from typsa.components.line import Line
from typsa.components.storage_unit import StorageUnit
from typsa.time_variation import Series, TimestampSnapshots
```


```python
pypsa_network = pypsa.examples.scigrid_de()

contingency_factor = 0.7
pypsa_network.lines.s_max_pu = contingency_factor
pypsa_network.lines.loc[["316", "527", "602"], "s_nom"] = 1715

pypsa_network.generators["control"] = "PV"
pypsa_network.generators.loc[pypsa_network.generators["bus"] == "492", "control"] = "PQ"

network = typsa.Network.from_pypsa_network(pypsa_network, TimestampSnapshots)
```

    INFO:pypsa.network.io:Retrieving network data from https://github.com/PyPSA/PyPSA/raw/v1.0.7/examples/networks/scigrid-de/scigrid-de.nc.
    INFO:pypsa.network.io:New version 1.1.2 available! (Current: 1.0.7)
    INFO:pypsa.network.io:Imported network 'SciGrid-DE' has buses, carriers, generators, lines, loads, storage_units, transformers



```python
generation_capacity_by_carrier: dict[str | None, float] = {}
for g in network.generators.values():
    if isinstance(g, Generator) and g.p_nom is not None:
        generation_capacity_by_carrier[g.carrier] = (
            generation_capacity_by_carrier.get(g.carrier, 0) + g.p_nom
        )
print(pd.Series(generation_capacity_by_carrier).round(1).to_frame("p_nom"))
```

                     p_nom
    Gas            23913.1
    Hard Coal      25312.6
    Run of River    3999.1
    Waste           1645.9
    Brown Coal     20879.5
    Oil             2710.2
    Storage Hydro   1445.0
    Other           3027.8
    Multiple         152.7
    Nuclear        12068.0
    Geothermal        31.7
    Wind Offshore   2973.5
    Wind Onshore   37339.9
    Solar          37041.5



```python
storage_capacity_by_carrier: dict[str | None, float] = {}
for su in network.storage_units.values():
    if isinstance(su, StorageUnit) and su.p_nom is not None:
        storage_capacity_by_carrier[su.carrier] = (
            storage_capacity_by_carrier.get(su.carrier, 0) + su.p_nom
        )
print(pd.Series(storage_capacity_by_carrier).round(1).to_frame("p_nom"))
```

                   p_nom
    Pumped Hydro  9179.5



```python
optimized_network = network.optimize_with_rolling_horizon(horizon=4, overlap=0)
```


```python
print(
    optimized_network.dynamic_results.of_all_generators.p.T.groupby(
        {g.name: g.carrier for g in optimized_network.generators.values()}
    )
    .sum()
    .T
)
```

    name                   Brown Coal          Gas  Geothermal     Hard Coal  \
    snapshot                                                                   
    2011-01-01 00:00:00   8954.695746   596.277945         0.0   9508.907684   
    2011-01-01 01:00:00   7740.822350   102.731042         0.0   8543.988561   
    2011-01-01 02:00:00   7453.596973    87.387948         0.0   6806.982171   
    2011-01-01 03:00:00   6969.683154    81.111447         0.0   5886.411673   
    2011-01-01 04:00:00   6438.037241    71.564784         0.0   4677.000222   
    2011-01-01 05:00:00   5928.410387    53.962358         0.0   2609.944440   
    2011-01-01 06:00:00   5842.342126    54.091201         0.0   2642.906648   
    2011-01-01 07:00:00   5532.020781    57.889006         0.0   2727.486778   
    2011-01-01 08:00:00   6053.121099     0.000000         0.0   1453.973538   
    2011-01-01 09:00:00   6101.341441     0.000000         0.0   1277.878373   
    2011-01-01 10:00:00   7267.499030     0.000000         0.0   2469.571971   
    2011-01-01 11:00:00   8433.374509     1.436970         0.0   3120.075144   
    2011-01-01 12:00:00  10410.047724     1.571761         0.0   5258.962156   
    2011-01-01 13:00:00   9631.795144    10.317455         0.0   5584.478813   
    2011-01-01 14:00:00  10243.019506    46.435863         0.0   7404.869785   
    2011-01-01 15:00:00  10934.330602   291.667170         0.0   9438.561993   
    2011-01-01 16:00:00  10255.393787  1264.713913        23.1  14755.931795   
    2011-01-01 17:00:00  10330.148501  1848.592494         0.0  15411.223954   
    2011-01-01 18:00:00  10633.526939  1484.478748         0.0  16419.324758   
    2011-01-01 19:00:00  10998.105390  1115.911618        23.1  13444.718534   
    2011-01-01 20:00:00  10761.419123  1158.694250        23.1  12434.915430   
    2011-01-01 21:00:00  10747.590958  1395.031800        23.1  12921.438233   
    2011-01-01 22:00:00  10885.064603   696.700090        23.1  10787.011136   
    2011-01-01 23:00:00  11007.938412   218.265854        23.1   8731.534765   
    
    name                 Multiple      Nuclear  Oil       Other  Run of River  \
    snapshot                                                                    
    2011-01-01 00:00:00       0.0  6929.058099  0.0  484.321958   3478.711742   
    2011-01-01 01:00:00       0.0  6812.822092  0.0  163.800000   3264.874716   
    2011-01-01 02:00:00       0.0  6843.580931  0.0   96.143184   3259.331331   
    2011-01-01 03:00:00       0.0  6851.723864  0.0   84.000000   3255.864157   
    2011-01-01 04:00:00       0.0  6862.446898  0.0   84.000000   3226.783526   
    2011-01-01 05:00:00       0.0  6882.994589  0.0   84.000000   3203.542323   
    2011-01-01 06:00:00       0.0  6904.288076  0.0   84.000000   3200.815581   
    2011-01-01 07:00:00       0.0  6914.922007  0.0   84.000000   3200.354720   
    2011-01-01 08:00:00       0.0  6594.984540  0.0   84.000000   3017.129984   
    2011-01-01 09:00:00       0.0  6592.873377  0.0   84.000000   3036.100000   
    2011-01-01 10:00:00       0.0  6592.833722  0.0  146.051396   3036.100000   
    2011-01-01 11:00:00       0.0  6711.253601  0.0  163.800000   3040.700000   
    2011-01-01 12:00:00       0.0  6700.123630  0.0  163.800000   3296.304156   
    2011-01-01 13:00:00       0.0  6825.439704  0.0  163.800000   3149.982795   
    2011-01-01 14:00:00       0.0  6884.398394  0.0  163.800000   3518.790175   
    2011-01-01 15:00:00       0.0  7271.498707  0.0  109.100000   3877.967656   
    2011-01-01 16:00:00       0.0  8387.101568  0.0  501.395142   3747.916963   
    2011-01-01 17:00:00       0.0  8422.239175  0.0  508.402524   3766.410703   
    2011-01-01 18:00:00       0.0  8382.358881  0.0  499.514879   3787.266427   
    2011-01-01 19:00:00       0.0  8383.916116  0.0  415.054114   3790.710662   
    2011-01-01 20:00:00       0.0  8526.056681  0.0  411.942446   3889.100000   
    2011-01-01 21:00:00       0.0  8499.983741  0.0  415.736287   3889.100000   
    2011-01-01 22:00:00       0.0  8417.463862  0.0  317.963566   3859.231374   
    2011-01-01 23:00:00       0.0  8318.074201  0.0  103.100000   3859.105521   
    
    name                       Solar  Storage Hydro        Waste  Wind Offshore  \
    snapshot                                                                      
    2011-01-01 00:00:00     0.000000    1214.523341  1203.500000     833.597295   
    2011-01-01 01:00:00     0.000000     837.478215  1241.000000     831.951710   
    2011-01-01 02:00:00     0.000000     839.315313  1241.000000     830.505463   
    2011-01-01 03:00:00     0.000000     840.192211  1230.126523    1314.015737   
    2011-01-01 04:00:00     0.000000     840.861571  1205.000000     828.354442   
    2011-01-01 05:00:00     0.000000     838.101836  1167.500000     825.961546   
    2011-01-01 06:00:00     0.000000     835.154121  1167.500000     884.506216   
    2011-01-01 07:00:00     0.000000     831.974585  1167.500000     886.495339   
    2011-01-01 08:00:00  3610.806206     818.607243  1167.500000     924.225598   
    2011-01-01 09:00:00  8145.332564     791.932762  1216.535366    1301.923128   
    2011-01-01 10:00:00  9499.211544     804.254454  1241.000000    1267.392644   
    2011-01-01 11:00:00  9637.470025    1197.246285  1241.000000    1259.590310   
    2011-01-01 12:00:00  7927.704868    1211.189852  1241.000000    1315.641240   
    2011-01-01 13:00:00  5322.057239    1218.392775  1241.000000    1364.541501   
    2011-01-01 14:00:00  1337.721285    1228.630028  1336.500000    1503.191725   
    2011-01-01 15:00:00     1.299145    1215.995513  1645.900000    1549.528161   
    2011-01-01 16:00:00     0.000000    1209.459321  1645.900000    1518.064064   
    2011-01-01 17:00:00     0.000000    1210.266962  1630.200000    1447.579306   
    2011-01-01 18:00:00     0.000000    1210.146578  1630.200000    1498.086283   
    2011-01-01 19:00:00     0.000000    1217.714703  1645.900000    1569.145516   
    2011-01-01 20:00:00     0.000000    1220.643588  1645.900000    1706.063137   
    2011-01-01 21:00:00     0.000000    1218.033533  1645.900000    1702.663741   
    2011-01-01 22:00:00     0.000000    1227.677674  1645.900000    1722.200004   
    2011-01-01 23:00:00     0.000000    1224.870822  1645.900000    1717.384666   
    
    name                 Wind Onshore  
    snapshot                           
    2011-01-01 00:00:00  18769.586192  
    2011-01-01 01:00:00  20223.951315  
    2011-01-01 02:00:00  20363.496686  
    2011-01-01 03:00:00  20764.351235  
    2011-01-01 04:00:00  20582.161858  
    2011-01-01 05:00:00  20025.162522  
    2011-01-01 06:00:00  20094.234962  
    2011-01-01 07:00:00  21033.736784  
    2011-01-01 08:00:00  21181.291832  
    2011-01-01 09:00:00  19438.722991  
    2011-01-01 10:00:00  18927.285240  
    2011-01-01 11:00:00  17746.041319  
    2011-01-01 12:00:00  15033.759638  
    2011-01-01 13:00:00  17041.611196  
    2011-01-01 14:00:00  17311.804245  
    2011-01-01 15:00:00  15617.959383  
    2011-01-01 16:00:00  14793.703012  
    2011-01-01 17:00:00  13683.453842  
    2011-01-01 18:00:00  10772.607469  
    2011-01-01 19:00:00  12051.282712  
    2011-01-01 20:00:00  13034.092571  
    2011-01-01 21:00:00  12978.857805  
    2011-01-01 22:00:00  12854.087692  
    2011-01-01 23:00:00  12373.605761  



```python
optimized_network.dynamic_results.of_all_storage_units.p.sum(axis="columns")
```




    snapshot
    2011-01-01 00:00:00    -219.100000
    2011-01-01 01:00:00    -219.100000
    2011-01-01 02:00:00    -219.100000
    2011-01-01 03:00:00    -821.000000
    2011-01-01 04:00:00    -102.450542
    2011-01-01 05:00:00    -119.100000
    2011-01-01 06:00:00    -185.838932
    2011-01-01 07:00:00    -219.100000
    2011-01-01 08:00:00     -76.520040
    2011-01-01 09:00:00     -98.800000
    2011-01-01 10:00:00       0.000000
    2011-01-01 11:00:00     -27.348162
    2011-01-01 12:00:00    -729.865025
    2011-01-01 13:00:00    -285.416620
    2011-01-01 14:00:00     184.678994
    2011-01-01 15:00:00     988.591670
    2011-01-01 16:00:00    -538.039566
    2011-01-01 17:00:00     166.282538
    2011-01-01 18:00:00    1186.649039
    2011-01-01 19:00:00     824.760632
    2011-01-01 20:00:00     -74.167226
    2011-01-01 21:00:00     -36.636098
    2011-01-01 22:00:00     170.000000
    2011-01-01 23:00:00       0.000000
    dtype: float64




```python
optimized_network.dynamic_results.of_all_storage_units.state_of_charge.sum(
    axis="columns"
)
```




    snapshot
    2011-01-01 00:00:00     208.145000
    2011-01-01 01:00:00     416.290000
    2011-01-01 02:00:00     624.435000
    2011-01-01 03:00:00    1404.385000
    2011-01-01 04:00:00    1501.713015
    2011-01-01 05:00:00    1614.858015
    2011-01-01 06:00:00    1791.405000
    2011-01-01 07:00:00    1999.550000
    2011-01-01 08:00:00    2072.244038
    2011-01-01 09:00:00    2166.104038
    2011-01-01 10:00:00    2166.104038
    2011-01-01 11:00:00    2175.845773
    2011-01-01 12:00:00    2869.217547
    2011-01-01 13:00:00    3140.363337
    2011-01-01 14:00:00    2937.628554
    2011-01-01 15:00:00    1897.005743
    2011-01-01 16:00:00    2389.323777
    2011-01-01 17:00:00    2190.957549
    2011-01-01 18:00:00     941.853297
    2011-01-01 19:00:00      73.684211
    2011-01-01 20:00:00     144.143075
    2011-01-01 21:00:00     178.947368
    2011-01-01 22:00:00       0.000000
    2011-01-01 23:00:00       0.000000
    dtype: float64




```python
now = dt.datetime.fromisoformat("2011-01-01 04:00:00")
loading = optimized_network.dynamic_results.of_all_lines.p0.loc[now] / pd.Series(
    {x.name: x.s_nom for x in optimized_network.lines.values() if isinstance(x, Line)}
)
print(loading.describe())
```

    count    852.000000
    mean      -0.003145
    std        0.260237
    min       -0.700000
    25%       -0.128281
    50%        0.003209
    75%        0.121985
    max        0.700000
    dtype: float64



```python
print(optimized_network.dynamic_results.of_all_buses.marginal_price.loc[now].describe())
```

    count    585.000000
    mean      15.737598
    std       10.941995
    min      -10.397824
    25%        6.992120
    50%       15.841190
    75%       25.048186
    max       52.150120
    Name: 2011-01-01 04:00:00, dtype: float64



```python
carrier = "Wind Onshore"
capacity = generation_capacity_by_carrier[carrier]
p_available = {
    g.name: g.p_max_pu.to_pandas() * g.p_nom
    for g in network.generators.values()
    if isinstance(g, Generator)
    and isinstance(g.p_max_pu, Series)
    and g.p_nom is not None
}
generators = network.generators
p_available_by_carrier = {
    c: sum(p_available.get(g.name, 0) for g in generators.values() if g.carrier == c)
    for c in network.carriers.keys()
}
p_by_carrier = (
    optimized_network.dynamic_results.of_all_generators.p.T.groupby(
        {g.name: g.carrier for g in network.generators.values()}
    )
    .sum()
    .T
)
p_curtailed_by_carrier = pd.DataFrame(p_available_by_carrier) - p_by_carrier
p_df = pd.DataFrame(
    {
        f"{carrier} capacity": capacity,
        f"{carrier} available": p_available_by_carrier[carrier],
        f"{carrier} dispatched": p_by_carrier[carrier],
        f"{carrier} curtailed": p_curtailed_by_carrier[carrier],
    }
)
```


```python
pf_results, pf_info = optimized_network.pf()
```


```python
print((~pf_info.converged).any().any())
```

    False



```python
print(
    (
        pf_results.of_all_lines.p0.loc[now]
        / pd.Series(
            {x.name: x.s_nom for x in network.lines.values() if isinstance(x, Line)}
        )
    ).describe()
)
```

    count    852.000000
    mean       0.000226
    std        0.262545
    min       -0.813767
    25%       -0.123980
    50%        0.003103
    75%        0.123851
    max        0.827600
    dtype: float64



```python
print((pypsa_network.lines_t.p0.loc[now] / pypsa_network.lines.s_nom).describe())
```

    count    0.0
    mean     NaN
    std      NaN
    min      NaN
    25%      NaN
    50%      NaN
    75%      NaN
    max      NaN
    dtype: float64



```python
pd.Series(
    {
        line.name: np.rad2deg(
            cast(float, pf_results.of_all_buses.v_ang.at[now, line.bus0])
            - cast(float, pf_results.of_all_buses.v_ang.at[now, line.bus1])
        )
        for line in network.lines.values()
    }
).describe()
```




    count    852.000000
    mean      -0.022249
    std        2.386780
    min      -12.158079
    25%       -0.465772
    50%        0.001604
    75%        0.534861
    max       17.959258
    dtype: float64




```python
print(cast(pd.Series, pf_results.of_all_buses.q.loc[now]).to_frame())
```

               2011-01-01 04:00:00
    name                          
    1                  -122.360489
    2                     0.000000
    3                   -43.669934
    4                  -118.776425
    5                     0.000000
    ...                        ...
    404_220kV           -13.676996
    413_220kV            -2.377202
    421_220kV           -12.830586
    450_220kV            -9.713586
    458_220kV           -12.147480
    
    [585 rows x 1 columns]

