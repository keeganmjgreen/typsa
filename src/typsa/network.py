from __future__ import annotations

import datetime as dt
from collections.abc import Callable
from copy import deepcopy
from typing import Any, Sequence, assert_never, cast

import pandas as pd
import pydantic
import pypsa
from linopy.constants import SolverStatus, TerminationCondition

from typsa._pypsa_network_derivative import PypsaNetworkDerivative
from typsa.components.bus import Bus, BusControl, SlackBusControl
from typsa.components.carrier import Carrier
from typsa.components.generator import (
    CommittableGenerator,
    ExtendableGenerator,
    Generator,
)
from typsa.components.global_constraint import GlobalConstraint
from typsa.components.line import BaseLine, ExtendableLine, Line
from typsa.components.link import CommittableLink, ExtendableLink, Link
from typsa.components.load import Load
from typsa.components.shunt_impedance import ShuntImpedance
from typsa.components.storage_unit import (
    ExtendableStorageUnit,
    StorageUnit,
)
from typsa.components.store import ExtendableStore, Store
from typsa.components.sub_network import SubNetwork
from typsa.components.transformer import (
    BaseTransformer,
    ExtendableTransformer,
    Transformer,
)
from typsa.results import (
    Capacities,
    LinearPowerFlowContingencyResults,
    LinearPowerFlowDynamicResults,
    NonlinearPowerFlowDynamicResults,
    OptimizationDynamicResults,
    OptimizationInfo,
    OptimizationStaticResults,
    PowerFlowInfo,
)
from typsa.time_variation import (
    IntegerSnapshots,
    RangedSeries,
    Static,
    TimestampedSeries,
    TimestampSnapshots,
)

from .components._base_component import (
    BaseComponent,
    BaseExtendableComponent,
    BusTiedComponentKeyed,
    Capacity,
    ComponentKeyed,
    ENom,
    PNom,
    SNom,
)


class _ComponentsAccessible[T: Static | TimestampSnapshots | IntegerSnapshots](
    PypsaNetworkDerivative[T]
):
    @property
    def buses(self) -> ComponentKeyed[dict[str, Bus[T]]]:
        """Get all `Bus` instances."""
        return ComponentKeyed(self._get_components(Bus, Bus[T]))

    @property
    def carriers(self) -> ComponentKeyed[dict[str, Carrier]]:
        """Get all `Carrier` instances."""
        return ComponentKeyed(self._get_components(Carrier, Carrier))

    @property
    def generators(
        self,
    ) -> BusTiedComponentKeyed[
        dict[str, Generator[T] | ExtendableGenerator[T] | CommittableGenerator[T]]
    ]:
        """Get all `Generator`, `ExtendableGenerator`, and `CommittableGenerator`
        instances.
        """
        components = (
            self._get_components(Generator, Generator[T])
            | self._get_components(ExtendableGenerator, ExtendableGenerator[T])
            | self._get_components(CommittableGenerator, CommittableGenerator[T])
        )
        return BusTiedComponentKeyed(
            components, components, list(self.buses.all.keys())
        )

    @property
    def global_constraints(self) -> ComponentKeyed[dict[str, GlobalConstraint]]:
        """Get all `GlobalConstraint` instances."""
        return ComponentKeyed(self._get_components(GlobalConstraint, GlobalConstraint))

    @property
    def lines(self) -> ComponentKeyed[dict[str, Line[T] | ExtendableLine[T]]]:
        """Get all `Line` and `ExtendableLine` instances."""
        return ComponentKeyed(
            self._get_components(Line, Line[T])
            | self._get_components(ExtendableLine, ExtendableLine[T])
        )

    @property
    def links(
        self,
    ) -> ComponentKeyed[dict[str, Link[T] | ExtendableLink[T] | CommittableLink[T]]]:
        """Get all `Link`, `ExtendableLink`, and `CommittableLink` instances."""
        return ComponentKeyed(
            self._get_components(Link, Link[T])
            | self._get_components(ExtendableLink, ExtendableLink[T])
            | self._get_components(CommittableLink, CommittableLink[T])
        )

    @property
    def loads(self) -> BusTiedComponentKeyed[dict[str, Load[T]]]:
        """Get all `Load` instances."""
        components = self._get_components(Load, Load[T])
        return BusTiedComponentKeyed(
            components, components, list(self.buses.all.keys())
        )

    @property
    def shunt_impedances(self) -> BusTiedComponentKeyed[dict[str, ShuntImpedance]]:
        """Get all `ShuntImpedance` instances."""
        components = self._get_components(ShuntImpedance, ShuntImpedance)
        return BusTiedComponentKeyed(
            components, components, list(self.buses.all.keys())
        )

    @property
    def storage_units(
        self,
    ) -> BusTiedComponentKeyed[dict[str, StorageUnit[T] | ExtendableStorageUnit[T]]]:
        """Get all `StorageUnit` and `ExtendableStorageUnit` instances."""
        components = self._get_components(
            StorageUnit, StorageUnit[T]
        ) | self._get_components(ExtendableStorageUnit, ExtendableStorageUnit[T])
        return BusTiedComponentKeyed(
            components, components, list(self.buses.all.keys())
        )

    @property
    def stores(
        self,
    ) -> BusTiedComponentKeyed[dict[str, Store[T] | ExtendableStore[T]]]:
        """Get all `Store` and `ExtendableStore` instances."""
        components = self._get_components(Store, Store[T]) | self._get_components(
            ExtendableStore, ExtendableStore[T]
        )
        return BusTiedComponentKeyed(
            components, components, list(self.buses.all.keys())
        )

    @property
    def transformers(
        self,
    ) -> ComponentKeyed[dict[str, Transformer[T] | ExtendableTransformer[T]]]:
        """Get all `Transformer` and `ExtendableTransformer` instances."""
        return ComponentKeyed(
            self._get_components(Transformer, Transformer[T])
            | self._get_components(ExtendableTransformer, ExtendableTransformer[T])
        )

    @property
    def plot(self) -> pypsa.plot.PlotAccessor:
        """Access plotting functionality."""
        return self._pypsa_network.plot

    @property
    def statistics(self) -> pypsa.statistics.StatisticsAccessor:
        """Access statistics functionality."""
        return self._pypsa_network.statistics


class _SubNetworksAccessible[T: Static | TimestampSnapshots | IntegerSnapshots](
    PypsaNetworkDerivative[T]
):
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
    PypsaNetworkDerivative[T]
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
        return self._get_optimization_results(
            pypsa_network_copy, solver_status, termination_condition
        )

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

        Optimization info is per-horizon and thus not returned. However, solver status
        and objective value are logged per-horizon.

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

    def optimize_security_constrained(
        self,
        snapshots: T | None = None,
        branch_outages: Sequence[BaseLine[T] | BaseTransformer[T]] | None = None,
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
        """Compute Security-Constrained Linear Optimal Power Flow (SCLOPF).

        Returns:
            Optimized network and optimization info.
        """

        pypsa_network_copy = self._copy_pypsa_network()
        solver_status, termination_condition = (
            pypsa_network_copy.optimize.optimize_security_constrained(  # pyright: ignore[reportUnknownMemberType]
                snapshots=(
                    snapshots.to_index()  # pyright: ignore[reportArgumentType]
                    if snapshots is not None
                    else None
                ),
                branch_outages=(
                    pd.MultiIndex.from_tuples(
                        [(branch.class_name, branch.name) for branch in branch_outages]
                    )
                    if branch_outages is not None
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
        )
        return self._get_optimization_results(
            pypsa_network_copy, solver_status, termination_condition
        )

    def _get_optimization_results(
        self,
        pypsa_network: pypsa.Network,
        solver_status: str,
        termination_condition: str,
    ) -> tuple[OptimizedNetwork[T], OptimizationInfo]:
        optimized_network = OptimizedNetwork(pypsa_network, self._snapshots_class)
        optimization_info = OptimizationInfo(
            solver_status=SolverStatus(solver_status),
            termination_condition=TerminationCondition(termination_condition),
            objective_value=pypsa_network.objective,
            objective_constant=cast(float, pypsa_network.objective_constant),
        )
        return optimized_network, optimization_info


class _Simulatable[T: Static | TimestampSnapshots | IntegerSnapshots](
    _ComponentsAccessible[T]
):
    def lpf(
        self,
        snapshots: T | None = None,
        skip_pre: bool = False,
    ) -> tuple[LinearPowerFlowDynamicResults[T], PowerFlowInfo]:
        """Run linearized power flow on the optimized network."""
        pypsa_network_copy = self._copy_pypsa_network()
        pypsa_network_copy.optimize.fix_optimal_capacities()
        pypsa_network_copy.optimize.fix_optimal_dispatch()
        info = pypsa_network_copy.lpf(  # pyright: ignore[reportUnknownMemberType]
            snapshots=(
                snapshots.to_index()  # pyright: ignore[reportArgumentType]
                if snapshots is not None
                else None
            ),
            skip_pre=skip_pre,
        )
        lpf_dynamic_results = LinearPowerFlowDynamicResults(
            ComponentsPortal(pypsa_network_copy, self._snapshots_class)
        )
        pf_info = PowerFlowInfo.model_validate(info)
        return lpf_dynamic_results, pf_info

    def pf(
        self,
        snapshots: T | None = None,
        skip_pre: bool = False,
        x_tol: float = 1e-6,
        use_seed: bool = False,
        distribute_slack: bool = False,
        slack_weights: str = "p_set",
    ) -> tuple[NonlinearPowerFlowDynamicResults[T], PowerFlowInfo]:
        """Run nonlinear power flow on the optimized network."""
        pypsa_network_copy = self._copy_pypsa_network()
        pypsa_network_copy.optimize.fix_optimal_capacities()
        pypsa_network_copy.optimize.fix_optimal_dispatch()
        info = pypsa_network_copy.pf(  # pyright: ignore[reportUnknownMemberType]
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
        pf_dynamic_results = NonlinearPowerFlowDynamicResults(
            ComponentsPortal(pypsa_network_copy, self._snapshots_class)
        )
        pf_info = PowerFlowInfo.model_validate(info)
        return pf_dynamic_results, pf_info

    def lpf_contingency(
        self,
        snapshots: T,
        branch_outages: Sequence[BaseLine[T] | BaseTransformer[T]] | None = None,
    ) -> LinearPowerFlowContingencyResults:
        """Run linear power flow on the optimized network for each of the specified
        branch outages in addition to the no-outage "base" case.
        """
        if len(snapshots.to_index()) != 1:
            raise ValueError(
                "pypsa.Network.lpf_contingency does not currently support multiple "
                "snapshots"
            )
        pypsa_network_copy = self._copy_pypsa_network()
        pypsa_network_copy.optimize.fix_optimal_capacities()
        pypsa_network_copy.optimize.fix_optimal_dispatch()
        df = pypsa_network_copy.lpf_contingency(  # pyright: ignore[reportUnknownMemberType]
            snapshots=snapshots.to_index()[0],  # pyright: ignore[reportArgumentType]
            branch_outages=(
                pd.MultiIndex.from_tuples(
                    [(branch.class_name, branch.name) for branch in branch_outages]
                )
                if branch_outages is not None
                else None
            ),  # pyright: ignore[reportArgumentType]
        )
        return LinearPowerFlowContingencyResults(
            base_case=df["base"].to_dict(),  # pyright: ignore[reportArgumentType]
            outage_cases=df.drop(columns=["base"]).to_dict(),  # pyright: ignore[reportArgumentType]
        )
        return df


class Network[T: Static | TimestampSnapshots | IntegerSnapshots = Static](
    _Optimizable[T], _Simulatable[T]
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
        for sub_dict_name in ["coordinates", "parameters"]:
            if sub_dict_name in kwargs:
                kwargs.update(kwargs.pop(sub_dict_name))
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
    _Optimizable[T], _Simulatable[T], _SubNetworksAccessible[T]
):
    pass


class OptimizedNetwork[T: Static | TimestampSnapshots | IntegerSnapshots = Static](
    _Simulatable[T], _SubNetworksAccessible[T]
):
    @property
    def all_capacities(self) -> Capacities:
        """Access capacities for components, whether extendable or non-extendable
        components.
        """
        capacities = deepcopy(self.static_results.capacities)
        capacities.generators.all.update(
            self._get_non_extendable_component_capacities(ExtendableGenerator, PNom)
        )
        capacities.lines.all.update(
            self._get_non_extendable_component_capacities(ExtendableLine, SNom)
        )
        capacities.links.all.update(
            self._get_non_extendable_component_capacities(ExtendableLink, PNom)
        )
        capacities.storage_units.all.update(
            self._get_non_extendable_component_capacities(ExtendableStorageUnit, PNom)
        )
        capacities.stores.all.update(
            self._get_non_extendable_component_capacities(ExtendableStore, ENom)
        )
        capacities.transformers.all.update(
            self._get_non_extendable_component_capacities(ExtendableTransformer, SNom)
        )
        return capacities

    def _get_non_extendable_component_capacities[T2: Capacity](
        self, component_class: type[BaseExtendableComponent], capacity_class: type[T2]
    ) -> dict[str, T2]:
        return {
            k: capacity_class(value=getattr(v, v.EXTENDABLE_COLUMN_PREFIX))
            for k, v in self._get_components(component_class, component_class).items()
            if not isinstance(v, ExtendableGenerator)
        }

    @property
    def static_results(self) -> OptimizationStaticResults[T]:
        """Access static optimization results."""
        return OptimizationStaticResults(self)

    @property
    def dynamic_results(self) -> OptimizationDynamicResults[T]:
        """Access dynamic optimization results."""
        return OptimizationDynamicResults(self)
