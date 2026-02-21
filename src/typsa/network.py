from __future__ import annotations

from collections.abc import Callable
from typing import cast

import pandas as pd
import pypsa
from pydantic.alias_generators import to_snake

from .components._base_component import (
    BaseComponent,
    BaseDynamicResults,
    BaseStaticResults,
)
from .components._component_names import SINGULAR_TO_PLURAL_COMPONENT_NAMES
from .components.bus import Bus, BusDynamicResults, BusStaticResults
from .components.generator import (
    BaseGenerator,
    CommittableGeneratorDynamicResults,
    ExtendableGeneratorStaticResults,
    GeneratorDynamicResults,
)
from .components.global_constraint import (
    GlobalConstraint,
    GlobalConstraintStaticResults,
)
from .components.line import (
    BaseLine,
    ExtendableLineStaticResults,
    LineDynamicResults,
    LineStaticResults,
)
from .components.link import (
    BaseLink,
    CommittableLinkDynamicResults,
    ExtendableLinkStaticResults,
    LinkDynamicResults,
)
from .components.load import Load, LoadDynamicResults
from .components.shunt_impedance import (
    ShuntImpedance,
    ShuntImpedanceDynamicResults,
    ShuntImpedanceStaticResults,
)
from .components.storage_unit import (
    BaseStorageUnit,
    ExtendableStorageUnitStaticResults,
    StorageUnitDynamicResults,
)
from .components.store import (
    BaseStore,
    ExtendableStoreStaticResults,
    StoreDynamicResults,
)
from .components.sub_network import SubNetwork, SubNetworkStaticResults
from .components.transformer import (
    BaseTransformer,
    ExtendableTransformerStaticResults,
    TransformerDynamicResults,
    TransformerStaticResults,
)


class Network(pypsa.Network):
    def add_component(self, component: BaseComponent) -> None:
        """Add a component to the network."""
        kwargs = component.model_dump(exclude_none=True)
        kwargs["class_name"] = component.class_name
        if "parameters" in kwargs:
            kwargs.update(kwargs.pop("parameters"))
        super().add(**kwargs)

    def add_components(self, *components: BaseComponent) -> None:
        """Add multiple components to the network."""
        for component in components:
            self.add_component(component)

    @property
    def static_results(self) -> NetworkStaticResults:
        """Access static optimization and simulation results."""
        return NetworkStaticResults(self)

    @property
    def dynamic_results(self) -> NetworkDynamicResults:
        """Access dynamic optimization and simulation results."""
        return NetworkDynamicResults(self)


class NetworkStaticResults:
    _network: pypsa.Network

    def __init__(self, network: pypsa.Network) -> None:
        self._network = network

    @property
    def all_buses(self) -> dict[str, BusStaticResults]:
        """Access static results for all `Bus` instances."""
        return self._static_results(Bus, BusStaticResults)

    @property
    def extendable_generators(
        self,
    ) -> dict[str, ExtendableGeneratorStaticResults]:
        """Access static results for all `ExtendableGenerator` instances."""
        return self._static_results(
            BaseGenerator,
            ExtendableGeneratorStaticResults,
            filter=(lambda df: df["p_nom_extendable"]),
        )

    @property
    def all_global_constraints(
        self,
    ) -> dict[str, GlobalConstraintStaticResults]:
        """Access static results for all `GlobalConstraint` instances."""
        return self._static_results(
            GlobalConstraint,
            GlobalConstraintStaticResults,
        )

    @property
    def all_lines(self) -> dict[str, LineStaticResults]:
        """Access static results for all lines, whether `ExtendableLine` instances or
        (non-extendable) `Line` instances.
        """
        return self._static_results(BaseLine, LineStaticResults)

    @property
    def lines(self) -> dict[str, LineStaticResults]:
        """Access static results for all `Line` instances."""
        return self._static_results(
            BaseLine,
            LineStaticResults,
            filter=(lambda df: df["s_nom_extendable"]),
        )

    @property
    def extendable_lines(self) -> dict[str, ExtendableLineStaticResults]:
        """Access static results for all `ExtendableLine` instances."""
        return self._static_results(
            BaseLine,
            ExtendableLineStaticResults,
            filter=(lambda df: ~df["s_nom_extendable"]),
        )

    @property
    def extendable_links(self) -> dict[str, ExtendableLinkStaticResults]:
        """Access static results for all `ExtendableLink` instances."""
        return self._static_results(
            BaseLink,
            ExtendableLinkStaticResults,
            filter=(lambda df: df["p_nom_extendable"]),
        )

    @property
    def all_shunt_impedances(
        self,
    ) -> dict[str, ShuntImpedanceStaticResults]:
        """Access static results for all `ShuntImpedance` instances."""
        return self._static_results(ShuntImpedance, ShuntImpedanceStaticResults)

    @property
    def extendable_storage_units(
        self,
    ) -> dict[str, ExtendableStorageUnitStaticResults]:
        """Access static results for all `ExtendableStorageUnit` instances."""
        return self._static_results(
            BaseStorageUnit,
            ExtendableStorageUnitStaticResults,
            filter=(lambda df: df["p_nom_extendable"]),
        )

    @property
    def extendable_stores(self) -> dict[str, ExtendableStoreStaticResults]:
        """Access static results for all `ExtendableStore` instances."""
        return self._static_results(
            BaseStore,
            ExtendableStoreStaticResults,
            filter=(lambda df: df["e_nom_extendable"]),
        )

    @property
    def all_sub_networks(self) -> dict[str, SubNetworkStaticResults]:
        """Access static results for all `SubNetwork` instances."""
        return self._static_results(SubNetwork, SubNetworkStaticResults)

    @property
    def all_transformers(self) -> dict[str, TransformerStaticResults]:
        """Access static results for all transformers, whether `ExtendableTransformer`
        instances or (non-extendable) `Transformer` instances.
        """
        return self._static_results(BaseTransformer, TransformerStaticResults)

    @property
    def transformers(self) -> dict[str, ExtendableTransformerStaticResults]:
        """Access static results for all `Transformers` instances."""
        return self._static_results(
            BaseTransformer,
            ExtendableTransformerStaticResults,
            filter=(lambda df: df["s_nom_extendable"]),
        )

    @property
    def extendable_transformers(
        self,
    ) -> dict[str, ExtendableTransformerStaticResults]:
        """Access static results for all `ExtendableTransformers` instances."""
        return self._static_results(
            BaseTransformer,
            ExtendableTransformerStaticResults,
            filter=(lambda df: df["s_nom_extendable"]),
        )

    def _static_results[T: BaseStaticResults](
        self,
        component_class: type[BaseComponent],
        static_results_class: type[T],
        filter: Callable[[pd.DataFrame], pd.Series] | None = None,
    ) -> dict[str, T]:
        static_df = _get_network_components(self._network, component_class).static
        if filter is not None:
            static_df = static_df.loc[filter(static_df)]
        return {
            cast(str, name): static_results_class.model_validate(dict(row))
            for name, row in static_df.iterrows()
        }

    def _get_components(self, component_class: type[BaseComponent]) -> pypsa.Components:
        return _get_network_components(self._network, component_class)


class NetworkDynamicResults:
    _network: pypsa.Network

    def __init__(self, network: pypsa.Network) -> None:
        self._network = network

    @property
    def all_buses(self) -> BusDynamicResults:
        """Access dynamic results for all `Bus` instances."""
        return self._dynamic_results(Bus, BusDynamicResults)

    @property
    def all_generators(self) -> GeneratorDynamicResults:
        """Access dynamic results for all generators, whether `CommittableGenerator`
        instances or (non-committable) `Generator`/`ExtendableGenerator` instances.
        """
        return self._dynamic_results(BaseGenerator, GeneratorDynamicResults)

    @property
    def generators(self) -> GeneratorDynamicResults:
        """Access dynamic results for all `Generator`/`ExtendableGenerator` instances."""
        return self._dynamic_results(
            BaseGenerator,
            GeneratorDynamicResults,
            filter=(lambda df: ~df["committable"]),
        )

    @property
    def committable_generators(self) -> CommittableGeneratorDynamicResults:
        """Access dynamic results for all `CommittableGenerator` instances."""
        return self._dynamic_results(
            BaseGenerator,
            CommittableGeneratorDynamicResults,
            filter=(lambda df: df["committable"]),
        )

    @property
    def all_lines(self) -> LineDynamicResults:
        """Access dynamic results for all `Line`/`ExtendableLine` instances."""
        return self._dynamic_results(BaseLine, LineDynamicResults)

    @property
    def all_links(self) -> LinkDynamicResults:
        """Access dynamic results for all links, whether `CommittableLink` instances or
        (non-committable) `Link`/`ExtendableLink` instances.
        """
        return self._dynamic_results(BaseLink, LinkDynamicResults)

    @property
    def links(self) -> LinkDynamicResults:
        """Access dynamic results for all `Link`/`ExtendableLink` instances."""
        return self._dynamic_results(
            BaseLink,
            LinkDynamicResults,
            filter=(lambda df: ~df["committable"]),
        )

    @property
    def committable_links(self) -> CommittableLinkDynamicResults:
        """Access dynamic results for all `CommittableLink` instances."""
        return self._dynamic_results(
            BaseLink,
            CommittableLinkDynamicResults,
            filter=(lambda df: df["committable"]),
        )

    @property
    def all_loads(self) -> LoadDynamicResults:
        """Access dynamic results for all `Load` instances."""
        return self._dynamic_results(Load, LoadDynamicResults)

    @property
    def all_shunt_impedances(self) -> ShuntImpedanceDynamicResults:
        """Access dynamic results for all `ShuntImpedance` instances."""
        return self._dynamic_results(ShuntImpedance, ShuntImpedanceDynamicResults)

    @property
    def all_storage_units(self) -> StorageUnitDynamicResults:
        """Access dynamic results for all `StorageUnit`/`ExtendableStorageUnit`
        instances.
        """
        return self._dynamic_results(BaseStorageUnit, StorageUnitDynamicResults)

    @property
    def all_stores(self) -> StoreDynamicResults:
        """Access dynamic results for all `Store`/`ExtendableStore` instances."""
        return self._dynamic_results(BaseStore, StoreDynamicResults)

    @property
    def all_transformers(self) -> TransformerDynamicResults:
        """Access dynamic results for all `Transformer`/`ExtendableTransformer`
        instances.
        """
        return self._dynamic_results(BaseTransformer, TransformerDynamicResults)

    def _dynamic_results[T: BaseDynamicResults](
        self,
        component_class: type[BaseComponent],
        dynamic_results_class: type[T],
        filter: Callable[[pd.DataFrame], pd.Series] | None = None,
    ) -> T:
        static_df = _get_network_components(self._network, component_class).static
        dynamic_dfs = cast(
            dict[str, pd.DataFrame],
            _get_network_components(self._network, component_class).dynamic,
        )
        if filter is not None:
            dynamic_dfs = {
                field_name: dynamic_dfs[field_name][
                    static_df.loc[filter(static_df)].index
                ]
                for field_name in dynamic_results_class.model_fields
            }
        return dynamic_results_class.model_validate(dynamic_dfs)


def _get_network_components(
    network: pypsa.Network, component_class: type[BaseComponent]
) -> pypsa.Components:
    with pypsa.option_context("api.new_components_api", True):
        return getattr(
            network,
            SINGULAR_TO_PLURAL_COMPONENT_NAMES[to_snake(component_class.class_name)],
        )
