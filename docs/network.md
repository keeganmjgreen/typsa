# Network

Like PyPSA, TyPSA provides a `Network` object.

`typsa.Network` is a drop-in replacement for `pypsa.Network`, providing identical functionality along with additional methods for adding TyPSA component objects and getting results. Under the hood, `typsa.Network` inherits from `pypsa.Network`. This allows you to switch to TyPSA in an existing project and try TyPSA out, without having to change all your code at once, because all your existing PyPSA-based code will function the same as before.

## Adding Components

Use `Network.add_component` and `Network.add_components` to add one or more components to the network.

## Getting Results

Use `Network.get_static_results` and `Network.get_dynamic_results` to get the static or dynamic results for a given component class, if applicable to that class. Your type checker will indicate the exact type of the object that will be returned, or if getting static and/or dynamic results would be invalid for a given component class.

### Examples

Get the static results for all buses:

``` py
n.get_static_results(Bus)
# Typed as `dict[str, BusStaticResults]`.
```

Get the dynamic results for all buses:

``` py
n.get_dynamic_results(Bus)
# Typed as `BusDynamicResults`.
```

---

Get the static results for all (non-extendable) generators:

``` py
n.get_static_results(Generator)
# Typed as `dict[str, GeneratorStaticResults]`.
```

Get the static results for all extendable generators:

``` py
n.get_static_results(ExtendableGenerator)
# Typed as `dict[str, ExtendableGeneratorStaticResults]`.
```

Get the static results for all generators, both extendable and non-extendable:

``` py
{**n.get_static_results(Generator), **n.get_static_results(ExtendableGenerator)}
# Typed as `dict[str, GeneratorStaticResults]` (common type to both).
```

---

Attempting to get the static results for the carrier component (invalid):

``` py
n.get_static_results(Carrier)
# Type checker complains.
```
