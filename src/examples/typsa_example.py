import typsa
from typsa.components import Bus, CustomLine, Generator, Load

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

line = CustomLine(
    name="line_1",
    bus0="zone_1",
    bus1="zone_2",
    x=0.01,
    s_nom=400,
)

n.add_components(zone_1, zone_2, load_1, load_2, gen_1, gen_2, line)

n.optimize()

n.results.buses.static

n.results.buses.dynamic.marginal_price
