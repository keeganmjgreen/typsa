from __future__ import annotations

from collections.abc import Callable
from typing import cast

import pandas as pd
import pypsa
from pydantic.alias_generators import to_snake

from typsa._pypsa_network_derivative import PypsaNetworkDerivative

from .components._base_component import (
    BaseComponent,
    BaseDynamicResults,
    BaseExtendableComponent,
    BaseStaticResults,
    Capacity,
)
from .components._component_names import SINGULAR_TO_PLURAL_COMPONENT_NAMES
from .components.bus import (
    Bus,
    BusNonlinearPfDynamicResults,
    BusOptimizationDynamicResults,
    BusOptimizationStaticResults,
    BusPfDynamicResults,
)
from .components.generator import (
    BaseGenerator,
    CommittableGeneratorOptimizationDynamicResults,
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
    LineNonlinearPfDynamicResults,
    LineOptimizationDynamicResults,
    LineOptimizationStaticResults,
    LinePfDynamicResults,
)
from .components.link import (
    BaseLink,
    CommittableLinkOptimizationDynamicResults,
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
    StorageUnitNonlinearPfDynamicResults,
    StorageUnitOptimizationDynamicResults,
    StorageUnitPfDynamicResults,
)
from .components.store import (
    BaseStore,
    StoreNonlinearPfDynamicResults,
    StoreOptimizationDynamicResults,
    StorePfDynamicResults,
)
from .components.sub_network import SubNetwork, SubNetworkOptimizationStaticResults
from .components.transformer import (
    BaseTransformer,
    TransformerNonlinearPfDynamicResults,
    TransformerOptimizationDynamicResults,
    TransformerOptimizationStaticResults,
    TransformerPfDynamicResults,
)


class OptimizationStaticResults(PypsaNetworkDerivative):
    @property
    def all_capacities(self) -> dict[str, Capacity]:
        """Access optimized capacities for all extendable components."""
        extendable_component_classes = [
            component
            for extendable_mixin in BaseExtendableComponent.__subclasses__()
            for component in extendable_mixin.__subclasses__()
        ]
        all_capacities: dict[str, Capacity] = {}
        for component_class in extendable_component_classes:
            static_df = _get_pypsa_network_components(
                self._pypsa_network, component_class
            ).static
            d = static_df.loc[
                static_df[f"{component_class.EXTENDABLE_COLUMN_PREFIX}_extendable"],
                f"{component_class.EXTENDABLE_COLUMN_PREFIX}_opt",
            ].to_dict()
            for component_name, capacity_value in d.items():
                all_capacities[cast(str, component_name)] = (
                    component_class.CAPACITY_TYPE(value=capacity_value)
                )
        return all_capacities

    def capacity_of(self, extendable_component: BaseExtendableComponent) -> Capacity:
        """Access the optimized capacity for an extendable component."""
        return self.all_capacities[extendable_component.name]

    @property
    def of_all_buses(self) -> dict[str, BusOptimizationStaticResults]:
        """Access static optimization results for all `Bus` instances."""
        return self._static_results(Bus, BusOptimizationStaticResults)

    def of_bus(self, bus: Bus) -> BusOptimizationStaticResults:
        """Access static optimization results for a `Bus` instance."""
        return self.of_all_buses[bus.name]

    @property
    def of_all_global_constraints(
        self,
    ) -> dict[str, GlobalConstraintOptimizationStaticResults]:
        """Access static optimization results for all `GlobalConstraint` instances."""
        return self._static_results(
            GlobalConstraint,
            GlobalConstraintOptimizationStaticResults,
        )

    def of_global_constraint(
        self, global_constraint: GlobalConstraint
    ) -> GlobalConstraintOptimizationStaticResults:
        """Access static optimization results for a `GlobalConstraint` instance."""
        return self.of_all_global_constraints[global_constraint.name]

    @property
    def of_all_lines(self) -> dict[str, LineOptimizationStaticResults]:
        """Access static optimization results for all `Line`/`ExtendableLine` instances."""
        return self._static_results(BaseLine, LineOptimizationStaticResults)

    def of_line(self, line: BaseLine) -> LineOptimizationStaticResults:
        """Access static optimization results for a `Line`/`ExtendableLine` instance."""
        return self.of_all_lines[line.name]

    @property
    def of_all_shunt_impedances(
        self,
    ) -> dict[str, ShuntImpedanceOptimizationStaticResults]:
        """Access static optimization results for all `ShuntImpedance` instances."""
        return self._static_results(
            ShuntImpedance, ShuntImpedanceOptimizationStaticResults
        )

    def of_shunt_impedance(
        self, shunt_impedance: ShuntImpedance
    ) -> ShuntImpedanceOptimizationStaticResults:
        """Access static optimization results for a `ShuntImpedance` instance."""
        return self.of_all_shunt_impedances[shunt_impedance.name]

    @property
    def of_all_sub_networks(self) -> dict[str, SubNetworkOptimizationStaticResults]:
        """Access static optimization results for all `SubNetwork` instances."""
        return self._static_results(SubNetwork, SubNetworkOptimizationStaticResults)

    def of_sub_network(
        self, sub_network: SubNetwork
    ) -> SubNetworkOptimizationStaticResults:
        """Access static optimization results for a `SubNetwork` instance."""
        return self.of_all_sub_networks[sub_network.name]

    @property
    def of_all_transformers(self) -> dict[str, TransformerOptimizationStaticResults]:
        """Access static optimization results for all
        `Transformer`/`ExtendableTransformer` instances.
        """
        return self._static_results(
            BaseTransformer, TransformerOptimizationStaticResults
        )

    def of_transformer(
        self, transformer: BaseTransformer
    ) -> TransformerOptimizationStaticResults:
        """Access static optimization results for a
        `Transformer`/`ExtendableTransformer` instance.
        """
        return self.of_all_transformers[transformer.name]

    def _static_results[T: BaseStaticResults](
        self,
        component_class: type[BaseComponent],
        static_results_class: type[T],
        filter: Callable[[pd.DataFrame], pd.Series] | None = None,
    ) -> dict[str, T]:
        static_df = _get_pypsa_network_components(
            self._pypsa_network, component_class
        ).static
        if filter is not None:
            static_df = static_df.loc[filter(static_df)]
        return {
            cast(str, name): static_results_class.model_validate(dict(row))
            for name, row in static_df.iterrows()
        }

    def _get_components(self, component_class: type[BaseComponent]) -> pypsa.Components:
        return _get_pypsa_network_components(self._pypsa_network, component_class)


class OptimizationDynamicResults(PypsaNetworkDerivative):
    @property
    def of_all_buses(self) -> BusOptimizationDynamicResults:
        """Access dynamic optimization results for all `Bus` instances."""
        return _get_dynamic_results(
            self._pypsa_network, Bus, BusOptimizationDynamicResults
        )

    @property
    def of_all_generators(self) -> GeneratorOptimizationDynamicResults:
        """Access dynamic optimization results for all generators, whether
        `CommittableGenerator` instances or (non-committable)
        `Generator`/`ExtendableGenerator` instances.
        """
        return _get_dynamic_results(
            self._pypsa_network,
            BaseGenerator,
            GeneratorOptimizationDynamicResults,
        )

    @property
    def of_generators(self) -> GeneratorOptimizationDynamicResults:
        """Access dynamic optimization results for all `Generator`/`ExtendableGenerator`
        instances.
        """
        return _get_dynamic_results(
            self._pypsa_network,
            BaseGenerator,
            GeneratorOptimizationDynamicResults,
            filter=(lambda df: ~df["committable"]),
        )

    @property
    def of_committable_generators(
        self,
    ) -> CommittableGeneratorOptimizationDynamicResults:
        """Access dynamic optimization results for all `CommittableGenerator` instances."""
        return _get_dynamic_results(
            self._pypsa_network,
            BaseGenerator,
            CommittableGeneratorOptimizationDynamicResults,
            filter=(lambda df: df["committable"]),
        )

    @property
    def of_all_lines(self) -> LineOptimizationDynamicResults:
        """Access dynamic optimization results for all `Line`/`ExtendableLine`
        instances.
        """
        return _get_dynamic_results(
            self._pypsa_network, BaseLine, LineOptimizationDynamicResults
        )

    @property
    def of_all_links(self) -> LinkOptimizationDynamicResults:
        """Access dynamic optimization results for all links, whether `CommittableLink`
        instances or (non-committable) `Link`/`ExtendableLink` instances.
        """
        return _get_dynamic_results(
            self._pypsa_network, BaseLink, LinkOptimizationDynamicResults
        )

    @property
    def of_links(self) -> LinkOptimizationDynamicResults:
        """Access dynamic optimization results for all `Link`/`ExtendableLink`
        instances.
        """
        return _get_dynamic_results(
            self._pypsa_network,
            BaseLink,
            LinkOptimizationDynamicResults,
            filter=(lambda df: ~df["committable"]),
        )

    @property
    def of_committable_links(self) -> CommittableLinkOptimizationDynamicResults:
        """Access dynamic optimization results for all `CommittableLink` instances."""
        return _get_dynamic_results(
            self._pypsa_network,
            BaseLink,
            CommittableLinkOptimizationDynamicResults,
            filter=(lambda df: df["committable"]),
        )

    @property
    def of_all_loads(self) -> LoadOptimizationDynamicResults:
        """Access dynamic optimization results for all `Load` instances."""
        return _get_dynamic_results(
            self._pypsa_network, Load, LoadOptimizationDynamicResults
        )

    @property
    def of_all_shunt_impedances(self) -> ShuntImpedanceOptimizationDynamicResults:
        """Access dynamic optimization results for all `ShuntImpedance` instances."""
        return _get_dynamic_results(
            self._pypsa_network,
            ShuntImpedance,
            ShuntImpedanceOptimizationDynamicResults,
        )

    @property
    def of_all_storage_units(self) -> StorageUnitOptimizationDynamicResults:
        """Access dynamic optimization results for all
        `StorageUnit`/`ExtendableStorageUnit` instances.
        """
        return _get_dynamic_results(
            self._pypsa_network,
            BaseStorageUnit,
            StorageUnitOptimizationDynamicResults,
        )

    @property
    def of_all_stores(self) -> StoreOptimizationDynamicResults:
        """Access dynamic optimization results for all `Store`/`ExtendableStore`
        instances.
        """
        return _get_dynamic_results(
            self._pypsa_network, BaseStore, StoreOptimizationDynamicResults
        )

    @property
    def of_all_transformers(self) -> TransformerOptimizationDynamicResults:
        """Access dynamic optimization results for all
        `Transformer`/`ExtendableTransformer` instances.
        """
        return _get_dynamic_results(
            self._pypsa_network,
            BaseTransformer,
            TransformerOptimizationDynamicResults,
        )


class LinearPowerFlowDynamicResults(PypsaNetworkDerivative):
    @property
    def of_all_buses(self) -> BusPfDynamicResults:
        """Access dynamic LPF results for all `Bus` instances."""
        return _get_dynamic_results(self._pypsa_network, Bus, BusPfDynamicResults)

    @property
    def of_all_generators(self) -> GeneratorPfDynamicResults:
        """Access dynamic LPF results for all
        `Generator`/`ExtendableGenerator`/`CommittableGenerator` instances.
        """
        return _get_dynamic_results(
            self._pypsa_network, BaseGenerator, GeneratorPfDynamicResults
        )

    @property
    def of_all_lines(self) -> LinePfDynamicResults:
        """Access dynamic LPF results for all `Line`/`ExtendableLine` instances."""
        return _get_dynamic_results(self._pypsa_network, BaseLine, LinePfDynamicResults)

    @property
    def of_all_links(self) -> LinkPfDynamicResults:
        """Access dynamic LPF results for all `Link`/`ExtendableLink`/`CommittableLink`
        instances.
        """
        return _get_dynamic_results(self._pypsa_network, BaseLink, LinkPfDynamicResults)

    @property
    def of_all_loads(self) -> LoadPfDynamicResults:
        """Access dynamic LPF results for all `Load` instances."""
        return _get_dynamic_results(self._pypsa_network, Load, LoadPfDynamicResults)

    @property
    def of_all_shunt_impedances(self) -> ShuntImpedancePfDynamicResults:
        """Access dynamic LPF results for all `ShuntImpedance` instances."""
        return _get_dynamic_results(
            self._pypsa_network,
            ShuntImpedance,
            ShuntImpedancePfDynamicResults,
        )

    @property
    def of_all_storage_units(self) -> StorageUnitPfDynamicResults:
        """Access dynamic LPF results for all `StorageUnit`/`ExtendableStorageUnit`
        instances.
        """
        return _get_dynamic_results(
            self._pypsa_network, BaseStorageUnit, StorageUnitPfDynamicResults
        )

    @property
    def of_all_stores(self) -> StorePfDynamicResults:
        """Access dynamic LPF results for all `Store`/`ExtendableStore` instances."""
        return _get_dynamic_results(
            self._pypsa_network, BaseStore, StorePfDynamicResults
        )

    @property
    def of_all_transformers(self) -> TransformerPfDynamicResults:
        """Access dynamic LPF results for all `Transformer`/`ExtendableTransformer`
        instances.
        """
        return _get_dynamic_results(
            self._pypsa_network,
            BaseTransformer,
            TransformerPfDynamicResults,
        )


class NonlinearPowerFlowDynamicResults(PypsaNetworkDerivative):
    @property
    def of_all_buses(self) -> BusNonlinearPfDynamicResults:
        """Access dynamic PF results for all `Bus` instances."""
        return _get_dynamic_results(
            self._pypsa_network, Bus, BusNonlinearPfDynamicResults
        )

    @property
    def of_all_generators(self) -> GeneratorNonlinearPfDynamicResults:
        """Access dynamic PF results for all
        `Generator`/`ExtendableGenerator`/`CommittableGenerator` instances.
        """
        return _get_dynamic_results(
            self._pypsa_network,
            BaseGenerator,
            GeneratorNonlinearPfDynamicResults,
        )

    @property
    def of_all_lines(self) -> LineNonlinearPfDynamicResults:
        """Access dynamic PF results for all `Line`/`ExtendableLine` instances."""
        return _get_dynamic_results(
            self._pypsa_network, BaseLine, LineNonlinearPfDynamicResults
        )

    @property
    def of_all_links(self) -> LinkNonlinearPfDynamicResults:
        """Access dynamic PF results for all `Link`/`ExtendableLink`/`CommittableLink`
        instances.
        """
        return _get_dynamic_results(
            self._pypsa_network, BaseLink, LinkNonlinearPfDynamicResults
        )

    @property
    def of_all_loads(self) -> LoadNonlinearPfDynamicResults:
        """Access dynamic PF results for all `Load` instances."""
        return _get_dynamic_results(
            self._pypsa_network, Load, LoadNonlinearPfDynamicResults
        )

    @property
    def of_all_shunt_impedances(self) -> ShuntImpedanceNonlinearPfDynamicResults:
        """Access dynamic PF results for all `ShuntImpedance` instances."""
        return _get_dynamic_results(
            self._pypsa_network,
            ShuntImpedance,
            ShuntImpedanceNonlinearPfDynamicResults,
        )

    @property
    def of_all_storage_units(self) -> StorageUnitNonlinearPfDynamicResults:
        """Access dynamic PF results for all `StorageUnit`/`ExtendableStorageUnit`
        instances.
        """
        return _get_dynamic_results(
            self._pypsa_network,
            BaseStorageUnit,
            StorageUnitNonlinearPfDynamicResults,
        )

    @property
    def of_all_stores(self) -> StoreNonlinearPfDynamicResults:
        """Access dynamic PF results for all `Store`/`ExtendableStore` instances."""
        return _get_dynamic_results(
            self._pypsa_network, BaseStore, StoreNonlinearPfDynamicResults
        )

    @property
    def of_all_transformers(self) -> TransformerNonlinearPfDynamicResults:
        """Access dynamic PF results for all `Transformer`/`ExtendableTransformer`
        instances.
        """
        return _get_dynamic_results(
            self._pypsa_network,
            BaseTransformer,
            TransformerNonlinearPfDynamicResults,
        )


def _get_pypsa_network_components(
    pypsa_network: pypsa.Network, component_class: type[BaseComponent]
) -> pypsa.Components:
    with pypsa.option_context("api.new_components_api", True):
        return getattr(
            pypsa_network,
            SINGULAR_TO_PLURAL_COMPONENT_NAMES[to_snake(component_class.class_name)],
        )


def _get_dynamic_results[T: BaseDynamicResults](
    pypsa_network: pypsa.Network,
    component_class: type[BaseComponent],
    dynamic_results_class: type[T],
    filter: Callable[[pd.DataFrame], pd.Series] | None = None,
) -> T:
    static_df = _get_pypsa_network_components(pypsa_network, component_class).static
    dynamic_dfs = cast(
        dict[str, pd.DataFrame],
        _get_pypsa_network_components(pypsa_network, component_class).dynamic,
    )
    if filter is not None:
        dynamic_dfs = {
            field_name: dynamic_dfs[field_name][static_df.loc[filter(static_df)].index]
            for field_name in dynamic_results_class.model_fields
        }
    return dynamic_results_class.model_validate(dynamic_dfs)
