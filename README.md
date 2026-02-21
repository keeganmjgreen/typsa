<div style="text-align: center; margin-right: 15px;"><img src="docs/logo/typsa_logo.svg"></img></div>

<h1 style="text-align: center;">TyPSA</h1>

[<div style="text-align: center;">Documentation</div>](https://keeganmjgreen.github.io)

TyPSA is a wrapper around the [PyPSA Python library for power systems analysis](https://docs.pypsa.org/latest/). TyPSA adds strong typing and data validation to PyPSA.

TyPSA provides:

- Classes for defining components of different types (`Bus`, `Load`, etc.) with their input data.
- A subclass of `pypsa.Network` &mdash; `typsa.Network` &mdash; to which components can be added. Optimizations and power flow simulations can be run using `typsa.Network.optimize()`, `typsa.Network.pf()`, etc.
- Accessors for obtaining static and dynamic model outputs (e.g., `typsa.Network.static_results.extendable_generators["g1"].p_nom_opt`).

## Usage Example

Example from [PyPSA Quickstart 1 &ndash; Markets](https://docs.pypsa.org/latest/examples/example-1/).

``` py
import typsa
from typsa.components import Bus, CustomLineParameters, Generator, Line, Load

n = typsa.Network()

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

n.add_components(zone_1, zone_2, load_1, load_2, gen_1, gen_2, line)

n.optimize()

n.static_results.all_buses
# {'zone_1': BusStaticResults(control='Slack', generator='gen_1', sub_network='0'),
#  'zone_2': BusStaticResults(control='PQ', generator='', sub_network='0')}

n.dynamic_results.all_buses.marginal_price
# name        zone_1    zone_2
# snapshot
# now       19.00009  35.00011
```
