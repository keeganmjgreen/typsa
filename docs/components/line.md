# Line

Use the `Line` class to represent a transmission or distribution line with a given apparent power capacity (`s_nom`).

Set `parameters=CustomLineParameters(...)` to represent a line with given values for series reactance (`x`), series resistance (`r`), shunt conductivity (`g`), and shunt susceptance (`b`).

Set `parameters=StandardLineParameters(...)` to represent a line with a [standard line type](https://docs.pypsa.org/stable/user-guide/components/line-types/), for which the `x`, `r`, `g`, and `b` values will be calculated automatically based on the line's `length` and number of parallel conductors (`num_parallel`).

Use the `ExtendableLine` class to represent a hypothetical line with an apparent power capacity that is flexible, in order to optimize its apparent power capacity (`ExtendableLineStaticResults.s_nom_opt`).

## API Reference

`Line` and `ExtendableLine` both inherit from the `BaseLine` parent class.

::: components.line
    options:
      inherited_members: false
      members_order: source
      show_labels: false
      show_root_toc_entry: false
      show_signature_annotations: true
      show_source: false
      members: ['CustomLineParameters', 'StandardLineParameters', 'BaseLine', 'Line', 'ExtendableLine', 'LineStaticResults', 'ExtendableLineStaticResults', 'LineDynamicResults']
