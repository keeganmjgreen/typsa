import pypsa
from pydantic.alias_generators import to_snake

from typsa.components._base_component import BaseComponent
from typsa.components._component_names import SINGULAR_TO_PLURAL_COMPONENT_NAMES


class PypsaNetworkDerivative:
    _pypsa_network: pypsa.Network

    def __init__(self, pypsa_network: pypsa.Network) -> None:
        self._pypsa_network = pypsa_network

    def _copy_pypsa_network(self) -> pypsa.Network:
        # Temporarily remove `solver_model`, as `pypsa.Network.copy` does not support
        # copying it:
        if (
            self._pypsa_network.model is not None  # pyright: ignore[reportUnnecessaryComparison] # Property `pypsa.Network.model` is typed incorrectly and can be `None`.
            and hasattr(self._pypsa_network.model, "solver_model")
        ):
            original_solver_model = self._pypsa_network.model.solver_model
            self._pypsa_network.model.solver_model = None
        else:
            original_solver_model = None

        copy = self._pypsa_network.copy()  # pyright: ignore[reportUnknownMemberType]

        if original_solver_model is not None:
            self._pypsa_network.model.solver_model = original_solver_model

        return copy

    def _get_pypsa_network_components(
        self, component_class: type[BaseComponent]
    ) -> pypsa.Components:
        with pypsa.option_context("api.new_components_api", True):
            return getattr(
                self._pypsa_network,
                SINGULAR_TO_PLURAL_COMPONENT_NAMES[
                    to_snake(component_class.class_name)
                ],
            )
