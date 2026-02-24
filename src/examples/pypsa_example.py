import pypsa

network = pypsa.Network()

network.add("Bus", name="zone_1")
network.add("Bus", name="zone_2")

network.add(
    "Load",
    name="load_1",
    bus="zone_1",
    p_set=500,
)
network.add(
    "Load",
    name="load_2",
    bus="zone_2",
    p_set=1500,
)

network.add(
    "Generator",
    name="gen_1",
    bus="zone_1",
    p_nom=2000,
    marginal_cost=10,
    marginal_cost_quadratic=0.005,
)
network.add(
    "Generator",
    name="gen_2",
    bus="zone_2",
    p_nom=2000,
    marginal_cost=13,
    marginal_cost_quadratic=0.01,
)

network.add(
    "Line",
    "line_1",
    bus0="zone_1",
    bus1="zone_2",
    x=0.01,
    s_nom=400,
)

network.optimize()

network.buses

network.buses_t["marginal_price"]
