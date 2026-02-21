# Transformer

Use the `Transformer` class to represent a transformer with a given apparent power capacity (`s_nom`).

Set `parameters=CustomTransformerParameters(...)` to represent a transformer with given values for series reactance (`x`), series resistance (`r`), shunt conductivity (`g`), shunt susceptance (`b`), `tap_ratio`, `tap_side`, and `phase_shift`.

Set `parameters=StandardTransformerParameters(...)` to represent a transformer with a [standard transformer type](https://docs.pypsa.org/stable/user-guide/components/transformer-types/), for which the `x`, `r`, etc. values will be calculated automatically based on the number of parallel transformers (`num_parallel`).

Use the `ExtendableTransformer` class to represent a hypothetical transformer with an apparent power capacity that is flexible, in order to optimize its apparent power capacity (`ExtendableTransformerStaticResults.s_nom_opt`).

## API Reference

`Transformer` and `ExtendableTransformer` both inherit from the `BaseTransformer` parent class.

::: components.transformer
    options:
      inherited_members: false
      members_order: source
      show_labels: false
      show_root_toc_entry: false
      show_signature_annotations: true
      show_source: false
      members: ['CustomTransformerParameters', 'StandardTransformerParameters', 'BaseTransformer', 'Transformer', 'ExtendableTransformer', 'TransformerStaticResults', 'ExtendableTransformerStaticResults', 'TransformerDynamicResults']
