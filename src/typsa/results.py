from __future__ import annotations

import dataclasses
from collections.abc import Callable
from typing import Literal, cast

import pandas as pd
import pydantic
from linopy.constants import SolverStatus, TerminationCondition

from typsa.components._base_component import BusTiedComponentKeyed, ComponentKeyed
from typsa.network import _ComponentsAccessible  # pyright: ignore[reportPrivateUsage]
from typsa.time_variation import IntegerSnapshots, Static, TimestampSnapshots

from .components._base_component import (
    BaseComponent,
    BaseDynamicResults,
    BaseExtendableComponent,
    BaseStaticResults,
    BusTied,
    Capacity,
    ENomOpt,
    PNomOpt,
    SNomOpt,
)
from .components.bus import (
    Bus,
    BusNonlinearPfDynamicResults,
    BusOptimizationDynamicResults,
    BusPfDynamicResults,
)
from .components.generator import (
    BaseGenerator,
    CommittableGeneratorOptimizationDynamicResults,
    ExtendableGenerator,
    GeneratorNonlinearPfDynamicResults,
    GeneratorOptimizationDynamicResults,
    GeneratorPfDynamicResults,
)
from .components.global_constraint import (
    GlobalConstraint,
    GlobalConstraintOptimizationStaticResults,
)
from .components.line import (
    BaseLine,
    ExtendableLine,
    LineNonlinearPfDynamicResults,
    LineOptimizationDynamicResults,
    LineOptimizationStaticResults,
    LinePfDynamicResults,
)
from .components.link import (
    BaseLink,
    CommittableLinkOptimizationDynamicResults,
    ExtendableLink,
    LinkNonlinearPfDynamicResults,
    LinkOptimizationDynamicResults,
    LinkPfDynamicResults,
)
from .components.load import (
    Load,
    LoadNonlinearPfDynamicResults,
    LoadOptimizationDynamicResults,
    LoadPfDynamicResults,
)
from .components.shunt_impedance import (
    ShuntImpedance,
    ShuntImpedanceNonlinearPfDynamicResults,
    ShuntImpedanceOptimizationDynamicResults,
    ShuntImpedanceOptimizationStaticResults,
    ShuntImpedancePfDynamicResults,
)
from .components.storage_unit import (
    BaseStorageUnit,
    ExtendableStorageUnit,
    StorageUnitNonlinearPfDynamicResults,
    StorageUnitOptimizationDynamicResults,
    StorageUnitPfDynamicResults,
)
from .components.store import (
    BaseStore,
    ExtendableStore,
    StoreNonlinearPfDynamicResults,
    StoreOptimizationDynamicResults,
    StorePfDynamicResults,
)
from .components.transformer import (
    BaseTransformer,
    ExtendableTransformer,
    TransformerNonlinearPfDynamicResults,
    TransformerOptimizationDynamicResults,
    TransformerOptimizationStaticResults,
    TransformerPfDynamicResults,
)


@dataclasses.dataclass
class Capacities:
    generators: BusTiedComponentKeyed[dict[str, PNomOpt]]
    lines: ComponentKeyed[dict[str, SNomOpt]]
    links: ComponentKeyed[dict[str, PNomOpt]]
    storage_units: BusTiedComponentKeyed[dict[str, PNomOpt]]
    stores: BusTiedComponentKeyed[dict[str, ENomOpt]]
    transformers: ComponentKeyed[dict[str, SNomOpt]]


@dataclasses.dataclass
class OptimizationStaticResults[T: Static | TimestampSnapshots | IntegerSnapshots]:
    _components_access: _ComponentsAccessible[T]

    @property
    def all_capacities(self) -> Capacities:
        """Access optimized capacities for all extendable components."""
        bus_names = list(self._components_access.buses.all.keys())
        return Capacities(
            generators=BusTiedComponentKeyed(
                self._get_component_capacities(ExtendableGenerator, PNomOpt),
                self._components_access.generators.all,
                bus_names,
            ),
            lines=ComponentKeyed(
                self._get_component_capacities(ExtendableLine, SNomOpt)
            ),
            links=ComponentKeyed(
                self._get_component_capacities(ExtendableLink, PNomOpt)
            ),
            storage_units=BusTiedComponentKeyed(
                self._get_component_capacities(ExtendableStorageUnit, PNomOpt),
                self._components_access.storage_units.all,
                bus_names,
            ),
            stores=BusTiedComponentKeyed(
                self._get_component_capacities(ExtendableStore, ENomOpt),
                self._components_access.stores.all,
                bus_names,
            ),
            transformers=ComponentKeyed(
                self._get_component_capacities(ExtendableTransformer, SNomOpt)
            ),
        )

    def _get_component_capacities[T2: Capacity](
        self, component_class: type[BaseExtendableComponent], capacity_class: type[T2]
    ) -> dict[str, T2]:
        static_df = self._components_access._get_pypsa_network_components(  # pyright: ignore[reportPrivateUsage]
            component_class
        ).static
        capacities = static_df.loc[
            static_df[f"{component_class.EXTENDABLE_COLUMN_PREFIX}_extendable"],
            f"{component_class.EXTENDABLE_COLUMN_PREFIX}_opt",
        ].to_dict()
        return {
            cast(str, component_name): capacity_class(value=capacity_value)
            for component_name, capacity_value in capacities.items()
        }

    @property
    def of_all_global_constraints(
        self,
    ) -> dict[str, GlobalConstraintOptimizationStaticResults]:
        """Access static optimization results for all `GlobalConstraint` instances."""
        return self._get_static_results(
            GlobalConstraint, GlobalConstraintOptimizationStaticResults
        )

    def of_global_constraint(
        self, global_constraint: GlobalConstraint
    ) -> GlobalConstraintOptimizationStaticResults:
        """Access static optimization results for a `GlobalConstraint` instance."""
        return self.of_all_global_constraints[global_constraint.name]

    @property
    def of_all_lines(self) -> ComponentKeyed[dict[str, LineOptimizationStaticResults]]:
        """Access static optimization results for all `Line`/`ExtendableLine` instances."""
        return ComponentKeyed(
            self._get_static_results(BaseLine, LineOptimizationStaticResults)
        )

    def of_line(self, line: BaseLine) -> LineOptimizationStaticResults:
        """Access static optimization results for a `Line`/`ExtendableLine` instance."""
        return self.of_all_lines.all[line.name]

    @property
    def of_all_shunt_impedances(
        self,
    ) -> BusTiedComponentKeyed[dict[str, ShuntImpedanceOptimizationStaticResults]]:
        """Access static optimization results for all `ShuntImpedance` instances."""
        return BusTiedComponentKeyed(
            self._get_static_results(
                ShuntImpedance, ShuntImpedanceOptimizationStaticResults
            ),
            self._components_access.shunt_impedances.all,
            list(self._components_access.buses.all.keys()),
        )

    def of_shunt_impedance(
        self, shunt_impedance: ShuntImpedance
    ) -> ShuntImpedanceOptimizationStaticResults:
        """Access static optimization results for a `ShuntImpedance` instance."""
        return self.of_all_shunt_impedances.all[shunt_impedance.name]

    @property
    def of_all_transformers(
        self,
    ) -> ComponentKeyed[dict[str, TransformerOptimizationStaticResults]]:
        """Access static optimization results for all
        `Transformer`/`ExtendableTransformer` instances.
        """
        return ComponentKeyed(
            self._get_static_results(
                BaseTransformer, TransformerOptimizationStaticResults
            )
        )

    def of_transformer(
        self, transformer: BaseTransformer
    ) -> TransformerOptimizationStaticResults:
        """Access static optimization results for a
        `Transformer`/`ExtendableTransformer` instance.
        """
        return self.of_all_transformers.all[transformer.name]

    def _get_static_results[T2: BaseStaticResults](
        self,
        component_class: type[BaseComponent],
        static_results_class: type[T2],
        filter: Callable[[pd.DataFrame], pd.Series] | None = None,
    ) -> dict[str, T2]:
        static_df = self._components_access._get_pypsa_network_components(  # pyright: ignore[reportPrivateUsage]
            component_class
        ).static
        if filter is not None:
            static_df = static_df.loc[filter(static_df)]
        return {
            cast(str, name): static_results_class.model_validate(dict(row))
            for name, row in static_df.iterrows()
        }


@dataclasses.dataclass
class _BaseDynamicResults[T: Static | TimestampSnapshots | IntegerSnapshots]:
    _components_access: _ComponentsAccessible[T]

    def _get_dynamic_results[T2: BaseDynamicResults](
        self,
        component_class: type[BaseComponent],
        dynamic_results_class: type[T2],
        filter: Callable[[pd.DataFrame], pd.Series] | None = None,
    ) -> T2:
        static_df = self._components_access._get_pypsa_network_components(  # pyright: ignore[reportPrivateUsage]
            component_class
        ).static
        dynamic_dfs = cast(
            dict[str, pd.DataFrame],
            self._components_access._get_pypsa_network_components(  # pyright: ignore[reportPrivateUsage]
                component_class
            ).dynamic,
        )
        if filter is not None:
            dynamic_dfs = {
                field_name: dynamic_dfs[field_name][
                    static_df.loc[filter(static_df)].index.intersection(
                        dynamic_dfs[field_name].columns
                    )
                ]
                for field_name in dynamic_results_class.model_fields
            }
        fields = {
            field_name: BusTiedComponentKeyed(
                df,
                self._components_access._get_components(component_class, BusTied),  # pyright: ignore[reportPrivateUsage]
                list(self._components_access.buses.all.keys()),
            )
            if issubclass(component_class, BusTied)
            else ComponentKeyed(df)
            for field_name, df in dynamic_dfs.items()
        }
        return dynamic_results_class.model_validate(fields)


class OptimizationDynamicResults[T: Static | TimestampSnapshots | IntegerSnapshots](
    _BaseDynamicResults[T]
):
    @property
    def of_all_buses(self) -> BusOptimizationDynamicResults:
        """Access dynamic optimization results for all `Bus` instances."""
        return self._get_dynamic_results(Bus, BusOptimizationDynamicResults)

    @property
    def of_all_generators(self) -> GeneratorOptimizationDynamicResults:
        """Access dynamic optimization results for all generators, whether
        `CommittableGenerator` instances or (non-committable)
        `Generator`/`ExtendableGenerator` instances.
        """
        return self._get_dynamic_results(
            BaseGenerator,
            GeneratorOptimizationDynamicResults,
        )

    @property
    def of_generators(self) -> GeneratorOptimizationDynamicResults:
        """Access dynamic optimization results for all `Generator`/`ExtendableGenerator`
        instances.
        """
        return self._get_dynamic_results(
            BaseGenerator,
            GeneratorOptimizationDynamicResults,
            filter=(lambda df: ~df["committable"]),
        )

    @property
    def of_committable_generators(
        self,
    ) -> CommittableGeneratorOptimizationDynamicResults:
        """Access dynamic optimization results for all `CommittableGenerator` instances."""
        return self._get_dynamic_results(
            BaseGenerator,
            CommittableGeneratorOptimizationDynamicResults,
            filter=(lambda df: df["committable"]),
        )

    @property
    def of_all_lines(self) -> LineOptimizationDynamicResults:
        """Access dynamic optimization results for all `Line`/`ExtendableLine`
        instances.
        """
        return self._get_dynamic_results(BaseLine, LineOptimizationDynamicResults)

    @property
    def of_all_links(self) -> LinkOptimizationDynamicResults:
        """Access dynamic optimization results for all links, whether `CommittableLink`
        instances or (non-committable) `Link`/`ExtendableLink` instances.
        """
        return self._get_dynamic_results(BaseLink, LinkOptimizationDynamicResults)

    @property
    def of_links(self) -> LinkOptimizationDynamicResults:
        """Access dynamic optimization results for all `Link`/`ExtendableLink`
        instances.
        """
        return self._get_dynamic_results(
            BaseLink,
            LinkOptimizationDynamicResults,
            filter=(lambda df: ~df["committable"]),
        )

    @property
    def of_committable_links(self) -> CommittableLinkOptimizationDynamicResults:
        """Access dynamic optimization results for all `CommittableLink` instances."""
        return self._get_dynamic_results(
            BaseLink,
            CommittableLinkOptimizationDynamicResults,
            filter=(lambda df: df["committable"]),
        )

    @property
    def of_all_loads(self) -> LoadOptimizationDynamicResults:
        """Access dynamic optimization results for all `Load` instances."""
        return self._get_dynamic_results(Load, LoadOptimizationDynamicResults)

    @property
    def of_all_shunt_impedances(self) -> ShuntImpedanceOptimizationDynamicResults:
        """Access dynamic optimization results for all `ShuntImpedance` instances."""
        return self._get_dynamic_results(
            ShuntImpedance, ShuntImpedanceOptimizationDynamicResults
        )

    @property
    def of_all_storage_units(self) -> StorageUnitOptimizationDynamicResults:
        """Access dynamic optimization results for all
        `StorageUnit`/`ExtendableStorageUnit` instances.
        """
        return self._get_dynamic_results(
            BaseStorageUnit, StorageUnitOptimizationDynamicResults
        )

    @property
    def of_all_stores(self) -> StoreOptimizationDynamicResults:
        """Access dynamic optimization results for all `Store`/`ExtendableStore`
        instances.
        """
        return self._get_dynamic_results(BaseStore, StoreOptimizationDynamicResults)

    @property
    def of_all_transformers(self) -> TransformerOptimizationDynamicResults:
        """Access dynamic optimization results for all
        `Transformer`/`ExtendableTransformer` instances.
        """
        return self._get_dynamic_results(
            BaseTransformer, TransformerOptimizationDynamicResults
        )


class OptimizationInfo(pydantic.BaseModel):
    solver_status: SolverStatus
    termination_condition: TerminationCondition
    objective_value: float | None
    objective_constant: float

    @property
    def total_system_cost(self) -> float | None:
        if self.objective_value is not None:
            return self.objective_value + self.objective_constant


class LinearPowerFlowDynamicResults[T: Static | TimestampSnapshots | IntegerSnapshots](
    _BaseDynamicResults[T]
):
    @property
    def of_all_buses(self) -> BusPfDynamicResults:
        """Access dynamic LPF results for all `Bus` instances."""
        return self._get_dynamic_results(Bus, BusPfDynamicResults)

    @property
    def of_all_generators(self) -> GeneratorPfDynamicResults:
        """Access dynamic LPF results for all
        `Generator`/`ExtendableGenerator`/`CommittableGenerator` instances.
        """
        return self._get_dynamic_results(BaseGenerator, GeneratorPfDynamicResults)

    @property
    def of_all_lines(self) -> LinePfDynamicResults:
        """Access dynamic LPF results for all `Line`/`ExtendableLine` instances."""
        return self._get_dynamic_results(BaseLine, LinePfDynamicResults)

    @property
    def of_all_links(self) -> LinkPfDynamicResults:
        """Access dynamic LPF results for all `Link`/`ExtendableLink`/`CommittableLink`
        instances.
        """
        return self._get_dynamic_results(BaseLink, LinkPfDynamicResults)

    @property
    def of_all_loads(self) -> LoadPfDynamicResults:
        """Access dynamic LPF results for all `Load` instances."""
        return self._get_dynamic_results(Load, LoadPfDynamicResults)

    @property
    def of_all_shunt_impedances(self) -> ShuntImpedancePfDynamicResults:
        """Access dynamic LPF results for all `ShuntImpedance` instances."""
        return self._get_dynamic_results(ShuntImpedance, ShuntImpedancePfDynamicResults)

    @property
    def of_all_storage_units(self) -> StorageUnitPfDynamicResults:
        """Access dynamic LPF results for all `StorageUnit`/`ExtendableStorageUnit`
        instances.
        """
        return self._get_dynamic_results(BaseStorageUnit, StorageUnitPfDynamicResults)

    @property
    def of_all_stores(self) -> StorePfDynamicResults:
        """Access dynamic LPF results for all `Store`/`ExtendableStore` instances."""
        return self._get_dynamic_results(BaseStore, StorePfDynamicResults)

    @property
    def of_all_transformers(self) -> TransformerPfDynamicResults:
        """Access dynamic LPF results for all `Transformer`/`ExtendableTransformer`
        instances.
        """
        return self._get_dynamic_results(BaseTransformer, TransformerPfDynamicResults)


class NonlinearPowerFlowDynamicResults[
    T: Static | TimestampSnapshots | IntegerSnapshots
](_BaseDynamicResults[T]):
    @property
    def of_all_buses(self) -> BusNonlinearPfDynamicResults:
        """Access dynamic PF results for all `Bus` instances."""
        return self._get_dynamic_results(Bus, BusNonlinearPfDynamicResults)

    @property
    def of_all_generators(self) -> GeneratorNonlinearPfDynamicResults:
        """Access dynamic PF results for all
        `Generator`/`ExtendableGenerator`/`CommittableGenerator` instances.
        """
        return self._get_dynamic_results(
            BaseGenerator, GeneratorNonlinearPfDynamicResults
        )

    @property
    def of_all_lines(self) -> LineNonlinearPfDynamicResults:
        """Access dynamic PF results for all `Line`/`ExtendableLine` instances."""
        return self._get_dynamic_results(BaseLine, LineNonlinearPfDynamicResults)

    @property
    def of_all_links(self) -> LinkNonlinearPfDynamicResults:
        """Access dynamic PF results for all `Link`/`ExtendableLink`/`CommittableLink`
        instances.
        """
        return self._get_dynamic_results(BaseLink, LinkNonlinearPfDynamicResults)

    @property
    def of_all_loads(self) -> LoadNonlinearPfDynamicResults:
        """Access dynamic PF results for all `Load` instances."""
        return self._get_dynamic_results(Load, LoadNonlinearPfDynamicResults)

    @property
    def of_all_shunt_impedances(self) -> ShuntImpedanceNonlinearPfDynamicResults:
        """Access dynamic PF results for all `ShuntImpedance` instances."""
        return self._get_dynamic_results(
            ShuntImpedance, ShuntImpedanceNonlinearPfDynamicResults
        )

    @property
    def of_all_storage_units(self) -> StorageUnitNonlinearPfDynamicResults:
        """Access dynamic PF results for all `StorageUnit`/`ExtendableStorageUnit`
        instances.
        """
        return self._get_dynamic_results(
            BaseStorageUnit, StorageUnitNonlinearPfDynamicResults
        )

    @property
    def of_all_stores(self) -> StoreNonlinearPfDynamicResults:
        """Access dynamic PF results for all `Store`/`ExtendableStore` instances."""
        return self._get_dynamic_results(BaseStore, StoreNonlinearPfDynamicResults)

    @property
    def of_all_transformers(self) -> TransformerNonlinearPfDynamicResults:
        """Access dynamic PF results for all `Transformer`/`ExtendableTransformer`
        instances.
        """
        return self._get_dynamic_results(
            BaseTransformer, TransformerNonlinearPfDynamicResults
        )


type PassiveBranch = Literal["Line", "Transformer"]
type PassiveBranchIdentifier = tuple[PassiveBranch, str]
type LinearPowerFlowContingencyCase = dict[PassiveBranchIdentifier, float]


class LinearPowerFlowContingencyResults(pydantic.BaseModel):
    base_case: LinearPowerFlowContingencyCase
    outage_cases: dict[PassiveBranchIdentifier, LinearPowerFlowContingencyCase]

    def to_df(self) -> pd.DataFrame:
        """Return a DataFrame with a row for each passive branch
        (PassiveBranchIdentifier) and a column for the base case and each outage case
        (Literal["base"] | PassiveBranchIdentifier).
        """
        return pd.concat(
            [pd.Series(self.base_case, name="base"), pd.DataFrame(self.outage_cases)],
            axis="columns",
        )


class PowerFlowInfo(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    n_iter: pd.DataFrame
    error: pd.DataFrame
    converged: pd.DataFrame
