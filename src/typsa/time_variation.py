import abc
import dataclasses
import datetime as dt
from collections.abc import Mapping, Sequence
from typing import Any, cast

import numpy as np
import pandas as pd


class _Snapshots(abc.ABC):
    @abc.abstractmethod
    def to_index(self) -> pd.Index:
        raise NotImplementedError


@dataclasses.dataclass
class TimestampSnapshots(_Snapshots):
    timestamps: Sequence[dt.datetime] | pd.DatetimeIndex

    def to_index(self) -> pd.Index:
        if isinstance(self.timestamps, pd.DatetimeIndex):
            return self.timestamps
        else:
            return pd.DatetimeIndex(list(self.timestamps))


@dataclasses.dataclass
class IntegerSnapshots(_Snapshots):
    integers: Sequence[int] | pd.RangeIndex | range
    spacing: dt.timedelta

    def to_index(self) -> pd.Index:
        if isinstance(self.integers, pd.RangeIndex):
            return self.integers
        else:
            return pd.Index(self.integers)


class Static(TimestampSnapshots, IntegerSnapshots):
    NOW = "now"

    def __init__(self) -> None:
        # The intersection of the set of possible timestamps and the set of possible
        # integers is empty, i.e., there is no value that is both a timestamp and an
        # integer:
        self.timestamps = []
        self.integers = []

        self.spacing = dt.timedelta()

    def to_index(self) -> pd.Index:
        return pd.Index([self.NOW])


class Series[T: TimestampSnapshots | IntegerSnapshots](abc.ABC):
    input: Mapping[Any, float] | pd.Series

    def __init__(self, input: Mapping[Any, float] | pd.Series) -> None:
        self.input = input
        if isinstance(self.input, pd.Series):
            if (
                self.input.dtype != np.dtype("float32")
                and self.input.dtype != np.dtype("float64")
                and self.input.dtype != np.dtype("int32")
                and self.input.dtype != np.dtype("int64")
            ):
                raise TypeError("Series data type must be float")

    @property
    @abc.abstractmethod
    def snapshots(self) -> T:
        raise NotImplementedError

    def to_pandas(self) -> pd.Series:
        if isinstance(self.input, pd.Series):
            return self.input
        else:
            return pd.Series(self.input)

    def __ge__(self, other: Any) -> bool:
        if isinstance(self.input, pd.Series):
            return all(self.input.ge(other))
        else:
            return all(v >= other for v in self.input.values())

    def __le__(self, other: Any) -> bool:
        if isinstance(self.input, pd.Series):
            return all(self.input.le(other))
        else:
            return all(v <= other for v in self.input.values())

    def __gt__(self, other: Any) -> bool:
        if isinstance(self.input, pd.Series):
            return all(self.input.gt(other))
        else:
            return all(v > other for v in self.input.values())

    def __lt__(self, other: Any) -> bool:
        if isinstance(self.input, pd.Series):
            return all(self.input.lt(other))
        else:
            return all(v < other for v in self.input.values())


class TimestampedSeries(Series[TimestampSnapshots]):
    input: Mapping[dt.datetime, float] | pd.Series

    def __init__(self, input: Mapping[dt.datetime, float] | pd.Series) -> None:
        super().__init__(input)
        if isinstance(self.input, pd.Series):
            if not isinstance(self.input.index, pd.DatetimeIndex):
                raise TypeError("Series index must be a DatetimeIndex")

    @property
    def snapshots(self) -> TimestampSnapshots:
        if isinstance(self.input, pd.Series):
            timestamps = cast(pd.DatetimeIndex, self.input.index)
        else:
            timestamps = list(self.input.keys())
        return TimestampSnapshots(timestamps)


class RangedSeries(Series[IntegerSnapshots]):
    input: Mapping[int, float] | pd.Series
    spacing: dt.timedelta

    def __init__(self, input: Mapping[int, float] | pd.Series) -> None:
        super().__init__(input)
        if isinstance(self.input, pd.Series):
            if not isinstance(self.input.index, pd.RangeIndex):
                raise TypeError("Series index must be a RangeIndex")

    @property
    def snapshots(self) -> IntegerSnapshots:
        if isinstance(self.input, pd.Series):
            integers = cast(pd.RangeIndex, self.input.index)
        else:
            integers = list(self.input.keys())
        return IntegerSnapshots(integers, self.spacing)
