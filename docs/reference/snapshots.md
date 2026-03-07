# Snapshots

## Network Snapshots

A `typsa.Network` can be optimized and simulated at one moment in time, called a *snapshot*, or across multiple snapshots. Snapshots can be timestamps or integers.

``` py
import typsa
from typsa.time_variation import TimestampSnapshots, IntegerSnapshots

# Typed as `Network[Static]`:
network = typsa.Network()

# Typed as `Network[TimestampSnapshots]`:
network = typsa.Network(
    TimestampSnapshots(
        <Sequence[dt.datetime] or pd.DatetimeIndex>,
    )
)

# Typed as `Network[IntegerSnapshots]`:
network = typsa.Network(
    IntegerSnapshots(
        <Sequence[int] | pd.RangeIndex | range>,
        spacing=<dt.timedelta>,
    )
)
```

## Component Snapshots

Most PyPSA (and thus TyPSA) component attributes accept time series data (indexed by timestamps or integers) in addition to accepting static data. For example:

``` py
from typsa.components import Generator

generator = Generator(
    name="generator",
    bus=...,
    p_nom=<float>,  # Can only be static value.
    p_min_pu=<float or TimestampedSeries or RangedSeries>,
    p_max_pu=<float or TimestampedSeries or RangedSeries>,
    # Note: TyPSA's Pydantic field validation works
    # whether float or TimestampedSeries or RangedSeries.
)
```

A `TimestampedSeries` is indexed by timestamps (corresponding to `TimestampSnapshots`), and a `RangedSeries` is indexed by integers (corresponding to `IntegerSnapshots`).

When defined with only static values, `generator` will by typed as `Generator[Static]`. When defined with at least one `TimestampedSeries` or `RangedSeries`, `generator` will be typed as `Generator[TimestampSnapshots]` or `Generator[IntegerSnapshots]`, respectively. One cannot mix-and-match `TimestampedSeries` and `RangedSeries` within a component (and thus, not within a `typsa.Network`, either).

`Generator[TimestampSnapshots]` can only be added to a network typed as `Network[TimestampSnapshots]`.  Likewise, `Generator[IntegerSnapshots]` can only be added to a network typed as `Network[IntegerSnapshots]`. `Generator[Static]` can be added to any network.

The above uses `Generator` as an example but applies to all TyPSA component types. This logic is enforced as part of type checking when using the TyPSA package, without having to run your code.

## API Reference

## `TimestampSnapshots`

``` py
snapshots = TimestampSnapshots(
    <Sequence[dt.datetime] or pd.DatetimeIndex>,
)
snapshots.timestamps  # Sequence[dt.datetime] or pd.DatetimeIndex
snapshots.to_index()  # pd.Index
```

## `IntegerSnapshots`

``` py
snapshots = IntegerSnapshots(
    <Sequence[int] or pd.RangeIndex or range>,
    spacing=<dt.timedelta>,
)
snapshots.integers  # Sequence[int] or pd.RangeIndex or range
snapshots.to_index()  # pd.Index
```

## `TimestampedSeries`

``` py
series = TimestampedSeries(<Mapping[dt.datetime, float] or pd.Series>)
series.input  # Mapping[dt.datetime, float] or pd.Series
series.snapshots  # TimestampSnapshots
```

## `RangedSeries`

``` py
series = RangedSeries(<Mapping[int, float] or pd.Series>)
series.input  # Mapping[int, float] or pd.Series
series.snapshots  # IntegerSnapshots
```
