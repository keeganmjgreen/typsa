from typing import ClassVar

from pydantic import BaseModel, ConfigDict


class BaseComponent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    class_name: ClassVar[str]


class BaseStaticResults(BaseModel):
    model_config = ConfigDict(extra="ignore")


class BaseDynamicResults(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
