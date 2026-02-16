# Line

Use the `CustomLine` class to represent a transmission or distribution line with given values for series reactance (`x`), series resistance (`r`), shunt conductivity (`g`), shunt susceptance (`b`), and apparent power capacity (`s_nom`).

Use the `StandardLine` class to represent a line with a [standard line type](https://docs.pypsa.org/stable/user-guide/components/line-types/), for which the `x`, `r`, `g`, and `b` values will be calculated automatically based on the line's `length` and number of parallel conductors (`num_parallel`).

Use the `ExtendableCustomLine` or `ExtendableStandardLine` class to represent a hypothetical line with an apparent power capacity that is flexible, in order to optimize its apparent power capacity (`LineStaticResults.s_nom_opt`).

## API Reference

The following table shows which parent classes each of the above classes inherits from.

|                                 | Parent: `BaseCustomLine` | Parent: `BaseStandardLine` |
|---------------------------------|--------------------------|----------------------------|
| Parent: `BaseNonExtendableLine` | `CustomLine`             | `StandardLine`             |
| Parent: `BaseExtendableLine`    | `ExtendableCustomLine`   | `ExtendableStandardLine`   |

`BaseCustomLine`, `BaseStandardLine`, `BaseExtendableCustomLine`, and `BaseExtendableStandardLine` all inherit from the `BaseLine` parent class.

::: components.line
    options:
      inherited_members: false
      members_order: source
      show_labels: false
      show_root_toc_entry: false
      show_signature_annotations: true
      show_source: false
      members: ['BaseLine', 'BaseStandardLine', 'BaseCustomLine', 'BaseNonExtendableLine', 'BaseExtendableLine', 'StandardLine', 'CustomLine', 'ExtendableStandardLine', 'ExtendableCustomLine', 'LineStaticResults', 'LineDynamicResults']
