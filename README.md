<div align="center">
    <img src="docs/logo/typsa_logo.svg">
</div>

<h1 align="center">TyPSA</h1>

<p align="center">
    <a href="https://keeganmjgreen.github.io">Documentation</a>
</p>

TyPSA is a wrapper around the [PyPSA Python library for power systems analysis](https://docs.pypsa.org/latest/). TyPSA adds strong typing and data validation to PyPSA.

TyPSA provides:

- Classes for defining [components](components/index.md) of different types ([`Bus`](components/bus.md), [`Load`](components/load.md), etc.) with their input data.
- APIs for defining a network, creating its optimization model, optimizing the network, and simulating power flow.
- Accessors for obtaining static and dynamic results of optimization and simulation.

## Usage Example

Example from [PyPSA Quickstart 1 &ndash; Markets](https://docs.pypsa.org/latest/examples/example-1/).

``` py
import typsa
from typsa.components import Bus, CustomLineParameters, Generator, Line, Load

network = typsa.Network()

zone_1 = Bus(name="zone_1")
zone_2 = Bus(name="zone_2")

load_1 = Load(
    name="load_1",
    bus=zone_1.name,
    p_set=500,
)
load_2 = Load(
    name="load_2",
    bus=zone_2.name,
    p_set=1500,
)

gen_1 = Generator(
    name="gen_1",
    bus=zone_1.name,
    p_nom=2000,
    marginal_cost=10,
    marginal_cost_quadratic=0.005,
)
gen_2 = Generator(
    name="gen_2",
    bus=zone_2.name,
    p_nom=2000,
    marginal_cost=13,
    marginal_cost_quadratic=0.01,
)

line = Line(
    name="line_1",
    bus0="zone_1",
    bus1="zone_2",
    parameters=CustomLineParameters(x=0.01),
    s_nom=400,
)

network.add_components(zone_1, zone_2, load_1, load_2, gen_1, gen_2, line)

optimized_network = network.model().optimize()

optimized_network.static_results.of_all_buses
# {'zone_1': BusOptimizationStaticResults(control='Slack', generator='gen_1', sub_network='0'),
#  'zone_2': BusOptimizationStaticResults(control='PQ', generator='', sub_network='0')}

optimized_network.dynamic_results.of_all_buses.marginal_price
# name        zone_1    zone_2
# snapshot
# now       19.00009  35.00011
```
