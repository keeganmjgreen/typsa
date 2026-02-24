from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from typing import Any, Self, Sequence

import linopy
import pandas as pd
import pypsa

from typsa._pypsa_network_derivative import PypsaNetworkDerivative
from typsa.results import (
    LinearPowerFlowDynamicResults,
    NonlinearPowerFlowDynamicResults,
    OptimizationDynamicResults,
    OptimizationStaticResults,
)

from .components._base_component import BaseComponent


class Network(PypsaNetworkDerivative):
    def __init__(self) -> None:
        super().__init__(pypsa.Network())

    @classmethod
    def from_pypsa_network(cls, pypsa_network: pypsa.Network) -> Self:
        """Create a `typsa.Network` from a `pypsa.Network`."""
        network = cls()
        network._pypsa_network = pypsa_network
        return network

    def add_components(self, *components: BaseComponent) -> None:
        """Add one or more components to the network."""
        for component in components:
            self._add_component(component)

    def _add_component(self, component: BaseComponent) -> None:
        kwargs = component.model_dump(exclude_none=True)
        kwargs["class_name"] = component.class_name
        if "parameters" in kwargs:
            kwargs.update(kwargs.pop("parameters"))
        self._pypsa_network.add(**kwargs)

    def model(
        self,
        snapshots: Sequence[Any] | None = None,
        multi_investment_periods: bool = False,
        transmission_losses: int = 0,
        linearized_unit_commitment: bool = False,
        consistency_check: bool = True,
        **kwargs: Any,
    ) -> NetworkOptimizationModel:
        """Create the network's optimization problem."""
        pypsa_network_copy = deepcopy(self._pypsa_network)
        pypsa_network_copy.optimize.create_model(  # pyright: ignore[reportUnknownMemberType]
            snapshots=snapshots,
            multi_investment_periods=multi_investment_periods,
            transmission_losses=transmission_losses,
            linearized_unit_commitment=linearized_unit_commitment,
            consistency_check=consistency_check,
            **kwargs,
        )
        return NetworkOptimizationModel(pypsa_network_copy)


class NetworkOptimizationModel(PypsaNetworkDerivative):
    @property
    def linopy_model(self) -> linopy.Model:
        return self._pypsa_network.model

    def optimize(
        self,
        extra_functionality: Callable[[pypsa.Network, pd.Index], None] | None = None,
        assign_all_duals: bool = False,
        solver_name: str | None = None,
        solver_options: dict[str, Any] | None = None,
        compute_infeasibilities: bool = False,
        **kwargs: Any,
    ) -> OptimizedNetwork:
        """Solve the network's optimization problem."""
        pypsa_network_copy = deepcopy(self._pypsa_network)
        pypsa_network_copy.optimize(
            extra_functionality=extra_functionality,
            assign_all_duals=assign_all_duals,
            solver_name=solver_name,
            solver_options=solver_options,
            compute_infeasibilities=compute_infeasibilities,
            **kwargs,
        )
        return OptimizedNetwork(pypsa_network_copy)


class OptimizedNetwork(PypsaNetworkDerivative):
    @property
    def static_results(self) -> OptimizationStaticResults:
        """Access static optimization results."""
        return OptimizationStaticResults(self._pypsa_network)

    @property
    def dynamic_results(self) -> OptimizationDynamicResults:
        """Access dynamic optimization results."""
        return OptimizationDynamicResults(self._pypsa_network)

    def simulation(
        self,
        snapshots: Sequence[Any] | None = None,
        skip_pre: bool = False,
    ) -> NetworkSimulationAccessor:
        """Access simulation methods."""
        return NetworkSimulationAccessor(
            self._pypsa_network, snapshots=snapshots, skip_pre=skip_pre
        )


class NetworkSimulationAccessor(PypsaNetworkDerivative):
    snapshots: Sequence[Any] | None
    skip_pre: bool

    def __init__(
        self,
        pypsa_network: pypsa.Network,
        snapshots: Sequence[Any] | None = None,
        skip_pre: bool = False,
    ) -> None:
        super().__init__(pypsa_network)
        self.snapshots = snapshots
        self.skip_pre = skip_pre

    def lpf(self) -> LinearPowerFlowDynamicResults:
        """Run linearized power flow on the optimized network."""
        pypsa_network_copy = deepcopy(self._pypsa_network)
        pypsa_network_copy.lpf(  # pyright: ignore[reportUnknownMemberType]
            snapshots=self.snapshots,
            skip_pre=self.skip_pre,
        )
        return LinearPowerFlowDynamicResults(pypsa_network_copy)

    def pf(
        self,
        x_tol: float = 1e-6,
        use_seed: bool = False,
        distribute_slack: bool = False,
        slack_weights: str = "p_set",
    ) -> NonlinearPowerFlowDynamicResults:
        """Run nonlinear power flow on the optimized network."""
        pypsa_network_copy = deepcopy(self._pypsa_network)
        pypsa_network_copy.pf(  # pyright: ignore[reportUnknownMemberType]
            snapshots=self.snapshots,
            skip_pre=self.skip_pre,
            x_tol=x_tol,
            use_seed=use_seed,
            distribute_slack=distribute_slack,
            slack_weights=slack_weights,
        )
        return NonlinearPowerFlowDynamicResults(pypsa_network_copy)
