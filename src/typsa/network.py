from typing import Mapping, cast, overload

import pandas as pd
import pypsa
from pydantic.alias_generators import to_snake

from .components import (
    bus,
    generator,
    global_constraint,
    line,
    link,
    load,
    shunt_impedance,
    storage_unit,
    store,
    sub_network,
    transformer,
)
from .components._base_component import (
    BaseComponent,
    BaseDynamicResults,
    BaseStaticResults,
)
from .components._component_names import SINGULAR_TO_PLURAL_COMPONENT_NAMES


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

    @overload
    def get_static_results(
        self, component_class: type[bus.Bus]
    ) -> dict[str, bus.BusStaticResults]: ...

    @overload
    def get_static_results(
        self, component_class: type[generator.ExtendableGenerator]
    ) -> dict[str, generator.ExtendableGeneratorStaticResults]: ...

    @overload
    def get_static_results(
        self, component_class: type[global_constraint.GlobalConstraint]
    ) -> dict[str, global_constraint.GlobalConstraintStaticResults]: ...

    @overload
    def get_static_results(
        self, component_class: type[line.Line]
    ) -> dict[str, line.LineStaticResults]: ...

    @overload
    def get_static_results(
        self, component_class: type[line.ExtendableLine]
    ) -> dict[str, line.ExtendableLineStaticResults]: ...

    @overload
    def get_static_results(
        self, component_class: type[link.ExtendableLink]
    ) -> dict[str, link.ExtendableLinkStaticResults]: ...

    @overload
    def get_static_results(
        self, component_class: type[shunt_impedance.ShuntImpedance]
    ) -> dict[str, shunt_impedance.ShuntImpedanceStaticResults]: ...

    @overload
    def get_static_results(
        self, component_class: type[storage_unit.ExtendableStorageUnit]
    ) -> dict[str, storage_unit.ExtendableStorageUnitStaticResults]: ...

    @overload
    def get_static_results(
        self, component_class: type[store.ExtendableStore]
    ) -> dict[str, store.ExtendableStoreStaticResults]: ...

    @overload
    def get_static_results(
        self, component_class: type[sub_network.SubNetwork]
    ) -> dict[str, sub_network.SubNetworkStaticResults]: ...

    @overload
    def get_static_results(
        self, component_class: type[transformer.Transformer]
    ) -> dict[str, transformer.TransformerStaticResults]: ...

    @overload
    def get_static_results(
        self, component_class: type[transformer.ExtendableTransformer]
    ) -> dict[str, transformer.ExtendableTransformerStaticResults]: ...

    def get_static_results(
        self, component_class: type[BaseComponent]
    ) -> Mapping[str, BaseStaticResults]:
        df = self._get_components(component_class).static

        if issubclass(component_class, bus.Bus):
            static_results_class = bus.BusStaticResults

        elif issubclass(component_class, generator.ExtendableGenerator):
            static_results_class = generator.ExtendableGeneratorStaticResults
            df = df[df["p_nom_extendable"]]

        elif issubclass(component_class, global_constraint.GlobalConstraint):
            static_results_class = global_constraint.GlobalConstraintStaticResults

        elif issubclass(component_class, line.Line):
            static_results_class = line.LineStaticResults
            df = df[~df["s_nom_extendable"]]
        elif issubclass(component_class, line.ExtendableLine):
            static_results_class = line.ExtendableLineStaticResults
            df = df[df["s_nom_extendable"]]

        elif issubclass(component_class, link.ExtendableLink):
            static_results_class = link.ExtendableLinkStaticResults
            df = df[df["p_nom_extendable"]]

        elif issubclass(component_class, shunt_impedance.ShuntImpedance):
            static_results_class = shunt_impedance.ShuntImpedanceStaticResults

        elif issubclass(component_class, storage_unit.ExtendableStorageUnit):
            static_results_class = storage_unit.ExtendableStorageUnitStaticResults
            df = df[df["p_nom_extendable"]]

        elif issubclass(component_class, store.ExtendableStore):
            static_results_class = store.ExtendableStoreStaticResults
            df = df[df["e_nom_extendable"]]

        elif issubclass(component_class, sub_network.SubNetwork):
            static_results_class = sub_network.SubNetworkStaticResults

        elif issubclass(component_class, transformer.Transformer):
            static_results_class = transformer.TransformerStaticResults
            df = df[~df["s_nom_extendable"]]
        elif issubclass(component_class, transformer.ExtendableTransformer):
            static_results_class = transformer.ExtendableTransformerStaticResults
            df = df[df["s_nom_extendable"]]

        else:
            raise TypeError

        return {
            cast(str, name): static_results_class.model_validate(dict(row))
            for name, row in df.iterrows()
        }

    @overload
    def get_dynamic_results(
        self, component_class: type[bus.Bus]
    ) -> bus.BusDynamicResults: ...

    @overload
    def get_dynamic_results(
        self, component_class: type[generator.CommittableGenerator]
    ) -> generator.CommittableGeneratorDynamicResults: ...

    @overload
    def get_dynamic_results(
        self, component_class: type[generator.Generator]
    ) -> generator.GeneratorDynamicResults: ...

    @overload
    def get_dynamic_results(
        self, component_class: type[line.Line]
    ) -> line.LineDynamicResults: ...

    @overload
    def get_dynamic_results(
        self, component_class: type[link.CommittableLink]
    ) -> link.CommittableLinkDynamicResults: ...

    @overload
    def get_dynamic_results(
        self, component_class: type[link.Link]
    ) -> link.LinkDynamicResults: ...

    @overload
    def get_dynamic_results(
        self, component_class: type[load.Load]
    ) -> load.LoadDynamicResults: ...

    @overload
    def get_dynamic_results(
        self, component_class: type[shunt_impedance.ShuntImpedance]
    ) -> shunt_impedance.ShuntImpedanceDynamicResults: ...

    @overload
    def get_dynamic_results(
        self, component_class: type[storage_unit.StorageUnit]
    ) -> storage_unit.StorageUnitDynamicResults: ...

    @overload
    def get_dynamic_results(
        self, component_class: type[store.Store]
    ) -> store.StoreDynamicResults: ...

    @overload
    def get_dynamic_results(
        self, component_class: type[transformer.Transformer]
    ) -> transformer.TransformerDynamicResults: ...

    def get_dynamic_results(
        self, component_class: type[BaseComponent]
    ) -> BaseDynamicResults:
        dfs = cast(
            dict[str, pd.DataFrame], self._get_components(component_class).dynamic
        )

        if issubclass(component_class, bus.Bus):
            dynamic_results_class = bus.BusDynamicResults

        # Must first check whether `CommittableGenerator` before widening the type to
        # `Generator`:
        elif issubclass(component_class, generator.CommittableGenerator):
            dynamic_results_class = generator.CommittableGeneratorDynamicResults
            dfs = {k: df[df["committable"]] for k, df in dfs.items()}
        elif issubclass(component_class, generator.Generator):
            dynamic_results_class = generator.GeneratorDynamicResults
            dfs = {k: df[~df["committable"]] for k, df in dfs.items()}

        elif issubclass(component_class, line.Line):
            dynamic_results_class = line.LineDynamicResults

        # Must first check whether `CommittableLink` before widening the type to `Link`:
        elif issubclass(component_class, link.CommittableLink):
            dynamic_results_class = link.CommittableLinkDynamicResults
            dfs = {k: df[df["committable"]] for k, df in dfs.items()}
        elif issubclass(component_class, link.Link):
            dynamic_results_class = link.LinkDynamicResults
            dfs = {k: df[~df["committable"]] for k, df in dfs.items()}

        elif issubclass(component_class, load.Load):
            dynamic_results_class = load.LoadDynamicResults

        elif issubclass(component_class, shunt_impedance.ShuntImpedance):
            dynamic_results_class = shunt_impedance.ShuntImpedanceDynamicResults

        elif issubclass(component_class, storage_unit.StorageUnit):
            dynamic_results_class = storage_unit.StorageUnitDynamicResults

        elif issubclass(component_class, store.Store):
            dynamic_results_class = store.StoreDynamicResults

        elif issubclass(component_class, transformer.Transformer):
            dynamic_results_class = transformer.TransformerDynamicResults

        else:
            raise TypeError

        return dynamic_results_class.model_validate(dfs)

    def _get_components(self, component_class: type[BaseComponent]) -> pypsa.Components:
        with pypsa.option_context("api.new_components_api", True):
            return getattr(
                self,
                SINGULAR_TO_PLURAL_COMPONENT_NAMES[
                    to_snake(component_class.class_name)
                ],
            )
