import math
from typing import cast

import pandas as pd
import pydantic
import pypsa
from pydantic.alias_generators import to_snake

from typsa.components._base_component import BaseComponent, BaseExtendableComponent
from typsa.components._component_names import SINGULAR_TO_PLURAL_COMPONENT_NAMES
from typsa.components.bus import Bus, Coordinates
from typsa.time_variation import (
    IntegerSnapshots,
    RangedSeries,
    Static,
    TimestampedSeries,
    TimestampSnapshots,
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

    def _get_components[T2](
        self, base_class: type[BaseComponent], type: type[T2]
    ) -> dict[str, T2]:
        static_df = self._get_pypsa_network_components(base_class).static
        if issubclass(base_class, BaseExtendableComponent):
            field_name = f"{base_class.EXTENDABLE_COLUMN_PREFIX}_extendable"
            static_df = cast(
                pd.DataFrame,
                static_df.loc[
                    static_df[field_name] == base_class.model_fields[field_name].default
                ],
            )
        committable = "committable"
        if committable in static_df.columns:
            static_df = cast(
                pd.DataFrame,
                static_df.loc[
                    static_df[committable]
                    == base_class.model_fields[committable].default
                ],
            )
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
