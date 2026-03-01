from typing import ClassVar

from pydantic import BaseModel, ConfigDict

from typsa.time_variation import IntegerSnapshots, Static, TimestampSnapshots


class BaseComponent[T: Static | TimestampSnapshots | IntegerSnapshots = Static](
    BaseModel
):
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    class_name: ClassVar[str]


class BaseStaticResults(BaseModel):
    model_config = ConfigDict(extra="ignore")


class BaseDynamicResults(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
