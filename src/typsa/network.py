from __future__ import annotations

import datetime as dt
from collections.abc import Callable
from typing import Any, Sequence, assert_never, cast

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
from typsa.time_variation import (
    IntegerSnapshots,
    RangedSeries,
    Static,
    TimestampedSeries,
    TimestampSnapshots,
)

from .components._base_component import BaseComponent


class Network[T: Static | TimestampSnapshots | IntegerSnapshots](
    PypsaNetworkDerivative
):
    def __init__(self, snapshots: T = Static()) -> None:
        """Create a `typsa.Network` with the given snapshots."""

        super().__init__(pypsa.Network())

        # Type annotation of `snapshots` argument of `pypsa.Network.set_snapshots`
        # is incorrect:
        index = cast(Sequence[Any], snapshots.to_index())
        match snapshots:
            case Static():
                pass
            case TimestampSnapshots():
                self._pypsa_network.set_snapshots(  # pyright: ignore[reportUnknownMemberType]
                    snapshots=index,
                    weightings_from_timedelta=True,
                )
            case IntegerSnapshots():
                self._pypsa_network.set_snapshots(  # pyright: ignore[reportUnknownMemberType]
                    snapshots=index,
                    default_snapshot_weightings=(
                        snapshots.spacing / dt.timedelta(hours=1)
                    ),
                )
            case _ as unreachable:
                assert_never(unreachable)

    @classmethod
    def from_pypsa_network[T2: Static | TimestampSnapshots | IntegerSnapshots](
        cls, pypsa_network: pypsa.Network, snapshots_class: type[T2]
    ) -> Network[T2]:
        """Create a `typsa.Network` from a `pypsa.Network`."""
        network = Network(
            snapshots=cls._snapshots_from_pypsa_network(pypsa_network, snapshots_class)
        )
        network._pypsa_network = pypsa_network
        return network

    @staticmethod
    def _snapshots_from_pypsa_network[
        T2: Static | TimestampSnapshots | IntegerSnapshots
    ](pypsa_network: pypsa.Network, snapshots_class: type[T2]) -> T2:
        unique_weighting_rows = pypsa_network.snapshot_weightings.drop_duplicates()
        if (
            len(unique_weighting_rows) != 1
            or len(unique_weightings := unique_weighting_rows.iloc[0].unique()) != 1
        ):
            raise ValueError("TyPSA expects all snapshot weightings to be the same")
        else:
            weighting = unique_weightings[0]

        if issubclass(snapshots_class, Static):
            snapshots = Static()
        elif issubclass(snapshots_class, TimestampSnapshots):
            if not isinstance(pypsa_network.snapshots, pd.DatetimeIndex):
                raise TypeError
            inferred_freq = pd.infer_freq(pypsa_network.snapshots)
            if inferred_freq is None:
                raise ValueError("TyPSA expects snapshots to have a uniform frequency")
            spacing = pd.Timedelta(pd.tseries.frequencies.to_offset(inferred_freq))  # pyright: ignore[reportArgumentType]
            spacing_hours = spacing / pd.Timedelta(hours=1)
            if weighting != spacing_hours:
                raise ValueError(
                    "TyPSA expects snapshot weightings (in hours) to match the "
                    "snapshot frequency"
                )
            snapshots = TimestampSnapshots(pypsa_network.snapshots)
        else:  # issubclass(snapshots_class, IntegerSnapshots)
            assert isinstance(pypsa_network.snapshots, pd.RangeIndex)
            spacing = weighting * dt.timedelta(hours=1)
            snapshots = IntegerSnapshots(pypsa_network.snapshots, spacing)

        return cast(T2, snapshots)

    @property
    def snapshots(self) -> T:
        snapshots = self._snapshots_from_pypsa_network(
            self._pypsa_network, self._snapshots_class
        )
        return snapshots

    def add_components(self, *components: BaseComponent[T]) -> None:
        """Add one or more components to the network."""
        for component in components:
            self._add_component(component)

    def _add_component(self, component: BaseComponent[T]) -> None:
        kwargs = dict(component)
        kwargs["class_name"] = component.class_name
        if "parameters" in kwargs:
            kwargs.update(kwargs.pop("parameters"))
        kwargs: dict[str, Any] = {
            k: v.input if isinstance(v, (TimestampedSeries, RangedSeries)) else v
            for k, v in kwargs.items()
            if v is not None
        }
        self._pypsa_network.add(**kwargs)

    def model(
        self,
        snapshots: Sequence[Any] | None = None,
        multi_investment_periods: bool = False,
        transmission_losses: int = 0,
        linearized_unit_commitment: bool = False,
        consistency_check: bool = True,
        **kwargs: Any,
    ) -> NetworkOptimizationModel[T]:
        """Create the network's optimization problem."""
        pypsa_network_copy = self._copy_pypsa_network()
        pypsa_network_copy.optimize.create_model(  # pyright: ignore[reportUnknownMemberType]
            snapshots=snapshots,
            multi_investment_periods=multi_investment_periods,
            transmission_losses=transmission_losses,
            linearized_unit_commitment=linearized_unit_commitment,
            consistency_check=consistency_check,
            **kwargs,
        )
        return NetworkOptimizationModel[T](pypsa_network_copy)


class NetworkOptimizationModel[
    T: Static | TimestampSnapshots | IntegerSnapshots = Static
](PypsaNetworkDerivative):
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
    ) -> OptimizedNetwork[T]:
        """Solve the network's optimization problem."""
        pypsa_network_copy = self._copy_pypsa_network()
        pypsa_network_copy.optimize(
            extra_functionality=extra_functionality,
            assign_all_duals=assign_all_duals,
            solver_name=solver_name,
            solver_options=solver_options,
            compute_infeasibilities=compute_infeasibilities,
            **kwargs,
        )
        return OptimizedNetwork[T](pypsa_network_copy)


class OptimizedNetwork[T: Static | TimestampSnapshots | IntegerSnapshots](
    PypsaNetworkDerivative
):
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
        pypsa_network_copy = self._copy_pypsa_network()
        pypsa_network_copy.optimize.fix_optimal_capacities()
        pypsa_network_copy.optimize.fix_optimal_dispatch()
        return NetworkSimulationAccessor(
            pypsa_network_copy, snapshots=snapshots, skip_pre=skip_pre
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
        pypsa_network_copy = self._copy_pypsa_network()
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
        pypsa_network_copy = self._copy_pypsa_network()
        pypsa_network_copy.pf(  # pyright: ignore[reportUnknownMemberType]
            snapshots=self.snapshots,
            skip_pre=self.skip_pre,
            x_tol=x_tol,
            use_seed=use_seed,
            distribute_slack=distribute_slack,
            slack_weights=slack_weights,
        )
        return NonlinearPowerFlowDynamicResults(pypsa_network_copy)
