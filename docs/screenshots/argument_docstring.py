

import typsa
from typsa.components import Bus, Load

n = typsa.Network()

n.add_components(Bus(name="zone_1"))
n.add_components(Bus(name="zone_2"))

n.add_components(
    Load(
        name="load_1",
        bus=
    )
)
