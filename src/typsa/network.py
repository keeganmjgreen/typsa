from __future__ import annotations

import datetime as dt
import math
from collections.abc import Callable
from typing import Any, Sequence, assert_never, cast

import pandas as pd
import pydantic
import pypsa
from linopy.constants import SolverStatus, TerminationCondition
from pypsa.plot import PlotAccessor

from typsa._pypsa_network_derivative import PypsaNetworkDerivative
from typsa.components.bus import Bus, BusControl, Coordinates, SlackBusControl
from typsa.components.carrier import Carrier
from typsa.components.generator import (
    CommittableGenerator,
    ExtendableGenerator,
    Generator,
)
from typsa.components.global_constraint import GlobalConstraint
from typsa.components.line import ExtendableLine, Line
from typsa.components.link import CommittableLink, ExtendableLink, Link
from typsa.components.load import Load
from typsa.components.shunt_impedance import ShuntImpedance
from typsa.components.storage_unit import ExtendableStorageUnit, StorageUnit
from typsa.components.store import ExtendableStore, Store
from typsa.components.sub_network import SubNetwork
from typsa.components.transformer import ExtendableTransformer, Transformer
from typsa.results import (
    LinearPowerFlowDynamicResults,
    NonlinearPowerFlowDynamicResults,
    OptimizationDynamicResults,
    OptimizationInfo,
    OptimizationStaticResults,
)
from typsa.time_variation import (
    IntegerSnapshots,
    RangedSeries,
    Static,
    TimestampedSeries,
    TimestampSnapshots,
)

from .components._base_component import BaseComponent, BaseExtendableComponent


class _HasSnapshotsClass[T: Static | TimestampSnapshots | IntegerSnapshots]:
    _snapshots_class: type[T]


class _ComponentsAccessible[T: Static | TimestampSnapshots | IntegerSnapshots](
    PypsaNetworkDerivative, _HasSnapshotsClass[T]
):
    def __init__(self, pypsa_network: pypsa.Network, snapshots_class: type[T]) -> None:
        super().__init__(pypsa_network)
        self._snapshots_class = snapshots_class

    @property
    def buses(self) -> dict[str, Bus[T]]:
        """Get all `Bus` instances."""
        return cast(dict[str, Bus[T]], self._get_components(Bus))

    @property
    def carriers(self) -> dict[str, Carrier]:
        """Get all `Carrier` instances."""
        return self._get_components(Carrier)

    @property
    def generators(
        self,
    ) -> dict[str, Generator[T] | ExtendableGenerator[T] | CommittableGenerator[T]]:
        """Get all `Generator`, `ExtendableGenerator`, and `CommittableGenerator`
        instances.
        """
        return {
            **cast(
                dict[str, Generator[T]],
                self._get_components(Generator),
            ),
            **cast(
                dict[str, ExtendableGenerator[T]],
                self._get_components(ExtendableGenerator),
            ),
            **cast(
                dict[str, CommittableGenerator[T]],
                self._get_components(CommittableGenerator),
            ),
        }

    @property
    def global_constraints(self) -> dict[str, GlobalConstraint]:
        """Get all `GlobalConstraint` instances."""
        return self._get_components(GlobalConstraint)

    @property
    def lines(self) -> dict[str, Line[T] | ExtendableLine[T]]:
        """Get all `Line` and `ExtendableLine` instances."""
        return {
            **cast(dict[str, Line[T]], self._get_components(Line)),
            **cast(dict[str, ExtendableLine[T]], self._get_components(ExtendableLine)),
        }

    @property
    def links(self) -> dict[str, Link[T] | ExtendableLink[T] | CommittableLink[T]]:
        """Get all `Link`, `ExtendableLink`, and `CommittableLink` instances."""
        return {
            **cast(dict[str, Link[T]], self._get_components(Link)),
            **cast(dict[str, ExtendableLink[T]], self._get_components(ExtendableLink)),
            **cast(
                dict[str, CommittableLink[T]], self._get_components(CommittableLink)
            ),
        }

    @property
    def loads(self) -> dict[str, Load]:
        """Get all `Load` instances."""
        return self._get_components(Load)

    @property
    def shunt_impedances(self) -> dict[str, ShuntImpedance]:
        """Get all `ShuntImpedance` instances."""
        return self._get_components(ShuntImpedance)

    @property
    def storage_units(self) -> dict[str, StorageUnit[T] | ExtendableStorageUnit[T]]:
        """Get all `StorageUnit` and `ExtendableStorageUnit` instances."""
        return {
            **cast(
                dict[str, StorageUnit[T]],
                self._get_components(StorageUnit),
            ),
            **cast(
                dict[str, ExtendableStorageUnit[T]],
                self._get_components(ExtendableStorageUnit),
            ),
        }

    @property
    def stores(self) -> dict[str, Store[T] | ExtendableStore[T]]:
        """Get all `Store` and `ExtendableStore` instances."""
        return {
            **cast(dict[str, Store[T]], self._get_components(Store)),
            **cast(
                dict[str, ExtendableStore[T]], self._get_components(ExtendableStore)
            ),
        }

    @property
    def transformers(self) -> dict[str, Transformer[T] | ExtendableTransformer[T]]:
        """Get all `Transformer` and `ExtendableTransformer` instances."""
        return {
            **cast(
                dict[str, Transformer[T]],
                self._get_components(Transformer),
            ),
            **cast(
                dict[str, ExtendableTransformer[T]],
                self._get_components(ExtendableTransformer),
            ),
        }

    def _get_components[T2: BaseComponent](
        self, component_class: type[T2]
    ) -> dict[str, T2]:
        static_df = self._get_pypsa_network_components(component_class).static
        if issubclass(component_class, BaseExtendableComponent):
            field_name = f"{component_class.EXTENDABLE_COLUMN_PREFIX}_extendable"
            static_df = cast(
                pd.DataFrame,
                static_df.loc[
                    static_df[field_name]
                    == component_class.model_fields[field_name].default
                ],
            )
        committable = "committable"
        if committable in static_df.columns:
            static_df = cast(
                pd.DataFrame,
                static_df.loc[
                    static_df[committable]
                    == component_class.model_fields[committable].default
                ],
            )
        component_dicts = {
            cast(str, name): dict(row) for name, row in static_df.iterrows()
        }
        dynamic_dfs = cast(
            dict[str, pd.DataFrame],
            self._get_pypsa_network_components(component_class).dynamic,
        )
        if issubclass(self._snapshots_class, Static):
            series_class = None
        elif issubclass(self._snapshots_class, TimestampSnapshots):
            series_class = TimestampedSeries
        else:
            assert issubclass(self._snapshots_class, IntegerSnapshots)
            series_class = RangedSeries
        for component_name in component_dicts.keys():
            component_dicts[component_name] = {
                k: (None if isinstance(v, str) and len(v) == 0 else v)
                for k, v in component_dicts[component_name].items()
                if not isinstance(v, float) or math.isfinite(v)
            }
            if (
                issubclass(component_class, Bus)
                and "x" in component_dicts[component_name]
                and "y" in component_dicts[component_name]
            ):
                component_dicts[component_name]["coordinates"] = Coordinates(
                    x=component_dicts[component_name].pop("x"),
                    y=component_dicts[component_name].pop("y"),
                )
            if "parameters" in component_class.model_fields:
                parameters_dict = {
                    k: component_dicts[component_name].pop(k)
                    for k in list(component_dicts[component_name].keys())
                    if k not in component_class.model_fields
                }
                component_dicts[component_name]["parameters"] = parameters_dict
            component_dicts[component_name]["name"] = component_name
            if series_class is not None:
                component_dicts[component_name].update(
                    {
                        field_name: series_class(dynamic_df[component_name])
                        for field_name, dynamic_df in dynamic_dfs.items()
                        if component_name in dynamic_df.columns
                        and any(dynamic_df[component_name].notna())
                    }
                )
        return {
            component_name: component_class.model_validate(
                component_dict, extra="ignore"
            )
            for component_name, component_dict in component_dicts.items()
        }

    @property
    def plot(self) -> PlotAccessor:
        """Access plotting functionality."""
        return self._pypsa_network.plot


class _SubNetworksAccessible(PypsaNetworkDerivative):
    @property
    def sub_networks(self) -> list[SubNetwork]:
        static_df = self._get_pypsa_network_components(SubNetwork).static
        return [
            SubNetwork.model_validate(dict(row), extra="ignore")
            for _, row in static_df.reset_index().iterrows()
        ]

    @property
    def control_by_bus(self) -> dict[str, BusControl | SlackBusControl]:
        static_df = self._get_pypsa_network_components(Bus).static
        bus_control_type_adapter = pydantic.TypeAdapter[BusControl | SlackBusControl](
            SlackBusControl | BusControl
        )
        return {
            cast(str, component_name): bus_control_type_adapter.validate_python(
                row["sub_network"]
            )
            for component_name, row in static_df.iterrows()
        }

    @property
    def sub_network_by_bus(self) -> dict[str, str]:
        return self._get_sub_network_by_component(Bus)

    @property
    def sub_network_by_line(self) -> dict[str, str]:
        return self._get_sub_network_by_component(Line)

    @property
    def sub_network_by_transformer(self) -> dict[str, str]:
        return self._get_sub_network_by_component(Transformer)

    @property
    def buses_by_sub_network(self) -> dict[str, list[str]]:
        return self._get_components_by_sub_network(self.sub_network_by_bus)

    @property
    def lines_by_sub_network(self) -> dict[str, list[str]]:
        return self._get_components_by_sub_network(self.sub_network_by_line)

    @property
    def transformers_by_sub_network(self) -> dict[str, list[str]]:
        return self._get_components_by_sub_network(self.sub_network_by_transformer)

    @property
    def branches_by_sub_network(self) -> dict[str, list[str]]:
        return self._get_components_by_sub_network(
            {**self.sub_network_by_line, **self.sub_network_by_transformer}
        )

    def _get_sub_network_by_component(
        self, component_class: type[Bus | Line | Transformer]
    ) -> dict[str, str]:
        static_df = self._get_pypsa_network_components(component_class).static
        return {
            cast(str, component_name): cast(str, row["sub_network"])
            for component_name, row in static_df.iterrows()
        }

    def _get_components_by_sub_network(
        self, sub_network_by_component: dict[str, str]
    ) -> dict[str, list[str]]:
        components_by_sub_network: dict[str, list[str]] = {}
        for bus, sub_network in sub_network_by_component.items():
            components_by_sub_network.setdefault(sub_network, []).append(bus)
        return components_by_sub_network


class _Optimizable[T: Static | TimestampSnapshots | IntegerSnapshots](
    PypsaNetworkDerivative, _HasSnapshotsClass[T]
):
    def optimize(
        self,
        snapshots: T | None = None,
        multi_investment_periods: bool = False,
        transmission_losses: int = 0,
        linearized_unit_commitment: bool = False,
        extra_functionality: Callable[[pypsa.Network, pd.Index], None] | None = None,
        assign_all_duals: bool = False,
        solver_name: str | None = None,
        solver_options: dict[str, Any] | None = None,
        compute_infeasibilities: bool = False,
        **kwargs: Any,
    ) -> tuple[OptimizedNetwork[T], OptimizationInfo]:
        """Optimize the network (model and solve its optimization problem).

        Returns:
            Optimized network and optimization info.
        """

        pypsa_network_copy = self._copy_pypsa_network()
        solver_status, termination_condition = pypsa_network_copy.optimize(
            snapshots=(
                snapshots.to_index()  # pyright: ignore[reportArgumentType]
                if snapshots is not None
                else None
            ),
            multi_investment_periods=multi_investment_periods,
            transmission_losses=transmission_losses,
            linearized_unit_commitment=linearized_unit_commitment,
            extra_functionality=extra_functionality,
            assign_all_duals=assign_all_duals,
            solver_name=solver_name,
            solver_options=solver_options,
            compute_infeasibilities=compute_infeasibilities,
            **kwargs,
        )
        optimized_network = OptimizedNetwork(pypsa_network_copy, self._snapshots_class)
        optimization_info = OptimizationInfo(
            solver_status=SolverStatus(solver_status),
            termination_condition=TerminationCondition(termination_condition),
            objective_value=pypsa_network_copy.objective,
            objective_constant=cast(float, pypsa_network_copy.objective_constant),
        )
        return optimized_network, optimization_info

    def optimize_with_rolling_horizon(
        self,
        horizon: int,
        overlap: int = 0,
        snapshots: T | None = None,
        multi_investment_periods: bool = False,
        transmission_losses: int = 0,
        linearized_unit_commitment: bool = False,
        extra_functionality: Callable[[pypsa.Network, pd.Index], None] | None = None,
        assign_all_duals: bool = False,
        solver_name: str | None = None,
        solver_options: dict[str, Any] | None = None,
        compute_infeasibilities: bool = False,
        **kwargs: Any,
    ) -> OptimizedNetwork[T]:
        """Optimize the network in a rolling horizon fashion.

        Optimization info are per-horizon and thus not returned. However, solver status and
        objective value are logged per-horizon.

        Returns:
            Optimized network.
        """

        pypsa_network_copy = self._copy_pypsa_network()
        pypsa_network_copy.optimize.optimize_with_rolling_horizon(  # pyright: ignore[reportUnknownMemberType]
            snapshots=(
                snapshots.to_index()  # pyright: ignore[reportArgumentType]
                if snapshots is not None
                else None
            ),
            multi_investment_periods=multi_investment_periods,
            transmission_losses=transmission_losses,
            linearized_unit_commitment=linearized_unit_commitment,
            horizon=horizon,
            overlap=overlap,
            extra_functionality=extra_functionality,
            assign_all_duals=assign_all_duals,
            solver_name=solver_name,
            solver_options=solver_options,
            compute_infeasibilities=compute_infeasibilities,
            **kwargs,
        )
        return OptimizedNetwork(pypsa_network_copy, self._snapshots_class)


class _Simulatable[T: Static | TimestampSnapshots | IntegerSnapshots](
    PypsaNetworkDerivative
):
    def lpf(
        self,
        snapshots: T | None = None,
        skip_pre: bool = False,
    ) -> LinearPowerFlowDynamicResults:
        """Run linearized power flow on the optimized network."""
        pypsa_network_copy = self._copy_pypsa_network()
        pypsa_network_copy.optimize.fix_optimal_capacities()
        pypsa_network_copy.optimize.fix_optimal_dispatch()
        pypsa_network_copy.lpf(  # pyright: ignore[reportUnknownMemberType]
            snapshots=(
                snapshots.to_index()  # pyright: ignore[reportArgumentType]
                if snapshots is not None
                else None
            ),
            skip_pre=skip_pre,
        )
        return LinearPowerFlowDynamicResults(pypsa_network_copy)

    def pf(
        self,
        snapshots: T | None = None,
        skip_pre: bool = False,
        x_tol: float = 1e-6,
        use_seed: bool = False,
        distribute_slack: bool = False,
        slack_weights: str = "p_set",
    ) -> NonlinearPowerFlowDynamicResults:
        """Run nonlinear power flow on the optimized network."""
        pypsa_network_copy = self._copy_pypsa_network()
        pypsa_network_copy.optimize.fix_optimal_capacities()
        pypsa_network_copy.optimize.fix_optimal_dispatch()
        pypsa_network_copy.pf(  # pyright: ignore[reportUnknownMemberType]
            snapshots=(
                snapshots.to_index()  # pyright: ignore[reportArgumentType]
                if snapshots is not None
                else None
            ),
            skip_pre=skip_pre,
            x_tol=x_tol,
            use_seed=use_seed,
            distribute_slack=distribute_slack,
            slack_weights=slack_weights,
        )
        return NonlinearPowerFlowDynamicResults(pypsa_network_copy)


class Network[T: Static | TimestampSnapshots | IntegerSnapshots = Static](
    _ComponentsAccessible[T], _Optimizable[T], _Simulatable[T]
):
    def __init__(self, snapshots: T = Static()) -> None:
        """Create a `typsa.Network` with the given snapshots."""

        super().__init__(pypsa.Network(), type(snapshots))

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

    def determine_network_topology(
        self,
        investment_period: int | str | None = None,
        skip_isolated_buses: bool = False,
    ) -> TopologyDeterminedNetwork[T]:
        """Build `SubNetwork`s from topology."""
        pypsa_network_copy = self._copy_pypsa_network()
        pypsa_network_copy.determine_network_topology(
            investment_period=investment_period,
            skip_isolated_buses=skip_isolated_buses,
        )
        return TopologyDeterminedNetwork(pypsa_network_copy, self._snapshots_class)


class TopologyDeterminedNetwork[T: Static | TimestampSnapshots | IntegerSnapshots](
    _ComponentsAccessible[T], _Optimizable[T], _Simulatable[T], _SubNetworksAccessible
):
    pass


class OptimizedNetwork[T: Static | TimestampSnapshots | IntegerSnapshots = Static](
    _ComponentsAccessible[T], _Simulatable[T], _SubNetworksAccessible
):
    @property
    def static_results(self) -> OptimizationStaticResults:
        """Access static optimization results."""
        return OptimizationStaticResults(self._pypsa_network)

    @property
    def dynamic_results(self) -> OptimizationDynamicResults:
        """Access dynamic optimization results."""
        return OptimizationDynamicResults(self._pypsa_network)
