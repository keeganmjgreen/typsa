from pydantic import BaseModel, ConfigDict


class BaseComponent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    class_name: str


class BaseStaticResults(BaseModel):
    model_config = ConfigDict(extra="ignore")


class BaseDynamicResults(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)


class BaseResults:
    pass
