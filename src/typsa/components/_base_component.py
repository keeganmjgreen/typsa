import dataclasses
from typing import Any, ClassVar, Mapping

import pandas as pd
import pydantic
from pydantic import BaseModel, ConfigDict, Field

from typsa.time_variation import IntegerSnapshots, Static, TimestampSnapshots


class BaseComponent[T: Static | TimestampSnapshots | IntegerSnapshots = Static](
    BaseModel
):
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    class_name: ClassVar[str]

    name: str = Field(min_length=1)
    """Unique name."""


class BusTied(pydantic.BaseModel):
    bus: str = Field(min_length=1)
    """Name of bus to which the component is attached."""


@dataclasses.dataclass
class ComponentKeyed[T: dict[str, Any] | pd.DataFrame]:
    all: T


class BusTiedComponentKeyed[T: dict[str, Any] | pd.DataFrame](ComponentKeyed[T]):
    _components_by_bus: dict[str, list[str]]

    def __init__(
        self, collection: T, components: Mapping[str, BusTied], bus_names: list[str]
    ) -> None:
        super().__init__(collection)
        self._components_by_bus = {
            bus_name: [k for k, v in components.items() if v.bus == bus_name]
            for bus_name in bus_names
        }

    @property
    def grouped_by_bus(self) -> dict[str, T]:
        return {
            bus_name: type(self.all)(
                {cn: self.all[cn] for cn in component_names if cn in self.all}
            )
            for bus_name, component_names in self._components_by_bus.items()
        }


class Capacity(BaseModel):
    value: float


class PNomOpt(Capacity):
    pass


class SNomOpt(Capacity):
    pass


class ENomOpt(Capacity):
    pass


class BaseExtendableComponent[
    T: Static | TimestampSnapshots | IntegerSnapshots = Static
](BaseComponent[T]):
    EXTENDABLE_COLUMN_PREFIX: ClassVar[str]


class PNomExtendableComponent[
    T: Static | TimestampSnapshots | IntegerSnapshots = Static
](BaseExtendableComponent[T]):
    EXTENDABLE_COLUMN_PREFIX = "p_nom"


class SNomExtendableComponent[
    T: Static | TimestampSnapshots | IntegerSnapshots = Static
](BaseExtendableComponent[T]):
    EXTENDABLE_COLUMN_PREFIX = "s_nom"


class ENomExtendableComponent[
    T: Static | TimestampSnapshots | IntegerSnapshots = Static
](BaseExtendableComponent[T]):
    EXTENDABLE_COLUMN_PREFIX = "e_nom"


class BaseStaticResults(BaseModel):
    model_config = ConfigDict(extra="ignore")


class BaseDynamicResults(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
