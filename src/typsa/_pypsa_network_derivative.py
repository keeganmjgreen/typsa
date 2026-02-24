import pypsa


class PypsaNetworkDerivative:
    _pypsa_network: pypsa.Network

    def __init__(self, pypsa_network: pypsa.Network) -> None:
        self._pypsa_network = pypsa_network
