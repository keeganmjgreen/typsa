# Transformer

Use the `CustomTransformer` class to represent a transformer with given values for series reactance (`x`), series resistance (`r`), shunt conductivity (`g`), shunt susceptance (`b`), `tap_ratio`, `tap_side`, `phase_shift`, and apparent power capacity (`s_nom`).

Use the `StandardTransformer` class to represent a transformer with a [standard transformer type](https://docs.pypsa.org/stable/user-guide/components/transformer-types/), for which the `x`, `r`, etc. values will be calculated automatically based on the number of parallel transformers (`num_parallel`).

Use the `ExtendableCustomTransformer` or `ExtendableStandardTransformer` class to represent a hypothetical transformer with an apparent power capacity that is flexible, in order to optimize its apparent power capacity (`TransformerStaticResults.s_nom_opt`).

## API Reference

The following table shows which parent classes each of the above classes inherits from.

|                                        | Parent: `BaseCustomTransformer` | Parent: `BaseStandardTransformer` |
| -------------------------------------- | ------------------------------- | --------------------------------- |
| Parent: `BaseNonExtendableTransformer` | `CustomTransformer`             | `StandardTransformer`             |
| Parent: `BaseExtendableTransformer`    | `ExtendableCustomTransformer`   | `ExtendableStandardTransformer`   |

`BaseCustomTransformer`, `BaseStandardTransformer`, `BaseExtendableCustomTransformer`, and `BaseExtendableStandardTransformer` all inherit from the `BaseTransformer` parent class.

::: components.transformer
options:
inherited_members: false
members_order: source
show_labels: false
show_root_toc_entry: false
show_signature_annotations: true
show_source: false
members: ['BaseTransformer', 'BaseStandardTransformer', 'BaseCustomTransformer', 'BaseNonExtendableTransformer', 'BaseExtendableTransformer', 'StandardTransformer', 'CustomTransformer', 'ExtendableStandardTransformer', 'ExtendableCustomTransformer', 'TransformerStaticResults', 'TransformerDynamicResults']
