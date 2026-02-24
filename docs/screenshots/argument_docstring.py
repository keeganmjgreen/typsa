

import typsa
from typsa.components import Bus, Load

network = typsa.Network()

network.add_components(Bus(name="zone_1"))
network.add_components(Bus(name="zone_2"))

network.add_components(
    Load(
        name="load_1",
        bus=123
    )
)
