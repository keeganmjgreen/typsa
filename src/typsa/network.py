from typing import Any, cast

import pypsa

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
    BaseResults,
    BaseStaticResults,
)


class Network(pypsa.Network):
    def add_component(self, component: BaseComponent) -> None:
        """Add a component to the network."""
        super().add(**component.model_dump(exclude_none=True))

    def add_components(self, *components: BaseComponent) -> None:
        """Add multiple components to the network."""
        for component in components:
            self.add_component(component)

    @property
    def results(self):
        """Access optimization and simulation results."""
        return Results(self)


class Results:
    _network: Network

    def __init__(self, network: Network) -> None:
        self._network = network

    @property
    def buses(self) -> bus.BusResults:
        """Access results for buses."""
        return self._results(
            bus.BusResults,
            bus.BusStaticResults,
            bus.BusDynamicResults,
            "buses",
        )

    @property
    def generators(self) -> generator.GeneratorResults:
        """Access results for generators."""
        return self._results(
            generator.GeneratorResults,
            generator.GeneratorStaticResults,
            generator.GeneratorDynamicResults,
            "generators",
        )

    @property
    def global_constraints(self) -> global_constraint.GlobalConstraintResults:
        """Access results for global constraints."""
        return self._results(
            global_constraint.GlobalConstraintResults,
            global_constraint.GlobalConstraintStaticResults,
            None,
            "global_constraints",
        )

    @property
    def lines(self) -> line.LineResults:
        """Access results for lines."""
        return self._results(
            line.LineResults,
            line.LineStaticResults,
            line.LineDynamicResults,
            "lines",
        )

    @property
    def links(self) -> link.LinkResults:
        """Access results for links."""
        return self._results(
            link.LinkResults,
            link.LinkStaticResults,
            link.LinkDynamicResults,
            "links",
        )

    @property
    def loads(self) -> load.LoadResults:
        """Access results for loads."""
        return self._results(
            load.LoadResults,
            None,
            load.LoadDynamicResults,
            "loads",
        )

    @property
    def shunt_impedances(self) -> shunt_impedance.ShuntImpedanceResults:
        """Access results for shunt impedances."""
        return self._results(
            shunt_impedance.ShuntImpedanceResults,
            shunt_impedance.ShuntImpedanceStaticResults,
            shunt_impedance.ShuntImpedanceDynamicResults,
            "shunt_impedances",
        )

    @property
    def storage_units(self) -> storage_unit.StorageUnitResults:
        """Access results for storage units."""
        return self._results(
            storage_unit.StorageUnitResults,
            storage_unit.StorageUnitStaticResults,
            storage_unit.StorageUnitDynamicResults,
            "storage_units",
        )

    @property
    def stores(self) -> store.StoreResults:
        """Access results for stores."""
        return self._results(
            store.StoreResults,
            store.StoreStaticResults,
            store.StoreDynamicResults,
            "stores",
        )

    @property
    def sub_networks(self) -> sub_network.SubNetworkResults:
        """Access results for sub-networks."""
        return self._results(
            sub_network.SubNetworkResults,
            sub_network.SubNetworkStaticResults,
            None,
            "sub_networks",
        )

    @property
    def transformers(self) -> transformer.TransformerResults:
        """Access results for transformers."""
        return self._results(
            transformer.TransformerResults,
            transformer.TransformerStaticResults,
            transformer.TransformerDynamicResults,
            "transformers",
        )

    def _results[T: BaseResults](
        self,
        results_class: type[T],
        static_results_class: type[BaseStaticResults] | None,
        dynamic_results_class: type[BaseDynamicResults] | None,
        components_name: str,
    ) -> T:
        with pypsa.option_context("api.new_components_api", True):
            kwargs: dict[str, Any] = {}
            components = cast(pypsa.Components, getattr(self._network, components_name))
            if static_results_class is not None:
                kwargs["static"] = {
                    cast(str, name): static_results_class.model_validate(dict(row))
                    for name, row in components.static.iterrows()
                }
            if dynamic_results_class is not None:
                kwargs["dynamic"] = dynamic_results_class.model_validate(
                    components.dynamic
                )
            return results_class(**kwargs)
