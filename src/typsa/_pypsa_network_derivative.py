from __future__ import annotations

import math
from typing import cast

import pandas as pd
import pydantic
import pypsa
from pydantic.alias_generators import to_snake

from typsa.components._base_component import BaseComponent
from typsa.components._component_names import SINGULAR_TO_PLURAL_COMPONENT_NAMES
from typsa.components.bus import Bus, Coordinates
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
from typsa.components.transformer import ExtendableTransformer, Transformer
from typsa.time_variation import (
    IntegerSnapshots,
    RangedSeries,
    Static,
    TimestampedSeries,
    TimestampSnapshots,
)

from .components._base_component import (
    BaseExtendableComponent,
    BusTiedComponentKeyed,
    ComponentKeyed,
)


class PypsaNetworkDerivative[T: Static | TimestampSnapshots | IntegerSnapshots]:
    _pypsa_network: pypsa.Network
    _snapshots_class: type[T]

    def __init__(self, pypsa_network: pypsa.Network, snapshots_class: type[T]) -> None:
        self._pypsa_network = pypsa_network
        self._snapshots_class = snapshots_class

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


class ComponentsPortal[T: Static | TimestampSnapshots | IntegerSnapshots](
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

    def _get_components[T2](
        self, base_class: type[BaseComponent], type: type[T2]
    ) -> dict[str, T2]:
        static_df = self._get_pypsa_network_components(base_class).static
        if issubclass(base_class, BaseExtendableComponent):
            extendable_field_name = f"{base_class.EXTENDABLE_COLUMN_PREFIX}_extendable"
            extendable_field = base_class.model_fields[extendable_field_name]
            if isinstance(
                extendable_field.default, bool
            ):  # I.e., not `PydanticUndefined`.
                static_df = static_df.loc[
                    static_df[extendable_field_name] == extendable_field.default
                ]
        committable_field_name = "committable"
        if committable_field_name in static_df.columns:
            committable_field = base_class.model_fields[committable_field_name]
            if isinstance(
                committable_field.default, bool
            ):  # I.e., not `PydanticUndefined`.
                static_df = static_df.loc[
                    static_df[committable_field_name] == committable_field.default
                ]
        component_dicts = {
            cast(str, name): dict(row) for name, row in static_df.iterrows()
        }
        dynamic_dfs = cast(
            dict[str, pd.DataFrame],
            self._get_pypsa_network_components(base_class).dynamic,
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
                issubclass(base_class, Bus)
                and "x" in component_dicts[component_name]
                and "y" in component_dicts[component_name]
            ):
                component_dicts[component_name]["coordinates"] = Coordinates(
                    x=component_dicts[component_name].pop("x"),
                    y=component_dicts[component_name].pop("y"),
                )
            if "parameters" in base_class.model_fields:
                parameters_dict = {
                    k: component_dicts[component_name].pop(k)
                    for k in list(component_dicts[component_name].keys())
                    if k not in base_class.model_fields
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
            component_name: pydantic.TypeAdapter(type).validate_python(
                component_dict, extra="ignore"
            )
            for component_name, component_dict in component_dicts.items()
        }
