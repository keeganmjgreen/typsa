# Line

Use the [`Line`](#components.line.Line) class to represent a transmission or distribution line with a given apparent power capacity ([`s_nom`](#components.line.Line.s_nom)).

Set `parameters=CustomLineParameters(...)` to represent a line with given values for series reactance ([`x`](#components.line.CustomLineParameters.x)), series resistance ([`r`](#components.line.CustomLineParameters.r)), shunt conductivity ([`g`](#components.line.CustomLineParameters.g)) and shunt susceptance ([`b`](#components.line.CustomLineParameters.b)).

Set `parameters=StandardLineParameters(...)` to represent a line with a [standard line type](https://docs.pypsa.org/stable/user-guide/components/line-types/), for which the `x`, `r`, `g`, and `b` values will be calculated automatically based on the line's [`length`](#components.line.StandardLineParameters.length) and number of parallel conductors ([`num_parallel`](#components.line.StandardLineParameters.num_parallel)).

Use the [`ExtendableLine`](#components.line.ExtendableLine) class to represent a hypothetical line with an apparent power capacity that is flexible, in order to optimize its apparent power capacity ([`ExtendableLineOptimizationStaticResults.s_nom_opt`](#components.line.ExtendableLineOptimizationStaticResults.s_nom_opt)).

## API Reference

[`Line`](#components.line.Line) and [`ExtendableLine`](#components.line.ExtendableLine) both inherit from the [`BaseLine`](#components.line.BaseLine) parent class.

::: components.line
    options:
      inherited_members: false
      members_order: source
      show_labels: false
      show_root_toc_entry: false
      show_signature_annotations: true
      show_source: false
      members:
        - CustomLineParameters
        - StandardLineParameters
        - BaseLine
        - Line
        - ExtendableLine
        - LineOptimizationStaticResults
        - ExtendableLineOptimizationStaticResults
        - LineBaseDynamicResults
        - LineOptimizationDynamicResults
        - LinePfDynamicResults
        - LineNonlinearPfDynamicResults
