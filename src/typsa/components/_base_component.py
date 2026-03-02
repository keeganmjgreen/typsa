from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from typsa.time_variation import IntegerSnapshots, Static, TimestampSnapshots


class BaseComponent[T: Static | TimestampSnapshots | IntegerSnapshots = Static](
    BaseModel
):
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    class_name: ClassVar[str]

    name: str = Field(min_length=1)
    """Unique name."""


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
    CAPACITY_TYPE: ClassVar[type[Capacity]]
    EXTENDABLE_COLUMN_PREFIX: ClassVar[str]


class PNomExtendableComponent[
    T: Static | TimestampSnapshots | IntegerSnapshots = Static
](BaseExtendableComponent[T]):
    CAPACITY_TYPE: ClassVar = PNomOpt
    EXTENDABLE_COLUMN_PREFIX = "p_nom"


class SNomExtendableComponent[
    T: Static | TimestampSnapshots | IntegerSnapshots = Static
](BaseExtendableComponent[T]):
    CAPACITY_TYPE: ClassVar = SNomOpt
    EXTENDABLE_COLUMN_PREFIX = "s_nom"


class ENomExtendableComponent[
    T: Static | TimestampSnapshots | IntegerSnapshots = Static
](BaseExtendableComponent[T]):
    CAPACITY_TYPE: ClassVar = ENomOpt
    EXTENDABLE_COLUMN_PREFIX = "e_nom"


class BaseStaticResults(BaseModel):
    model_config = ConfigDict(extra="ignore")


class BaseDynamicResults(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
