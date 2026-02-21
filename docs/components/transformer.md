# Transformer

Use the [`Transformer`](#components.transformer.Transformer) class to represent a transformer with a given apparent power capacity ([`s_nom`](#components.transformer.Transformer.s_nom)).

Set `parameters=CustomTransformerParameters(...)` to represent a transformer with given values for series reactance ([`x`](#components.transformer.CustomTransformerParameters.x)), series resistance ([`r`](#components.transformer.CustomTransformerParameters.r)), shunt conductivity ([`g`](#components.transformer.CustomTransformerParameters.g)), shunt susceptance ([`b`](#components.transformer.CustomTransformerParameters.b)), [`tap_ratio`](#components.transformer.CustomTransformerParameters.tap_ratio), [`tap_side`](#components.transformer.CustomTransformerParameters.tap_side), and [`phase_shift`](#components.transformer.CustomTransformerParameters.phase_shift).

Set `parameters=StandardTransformerParameters(...)` to represent a transformer with a [standard transformer type](https://docs.pypsa.org/stable/user-guide/components/transformer-types/), for which the `x`, `r`, etc. values will be calculated automatically based on the number of parallel transformers ([`num_parallel`](#components.transformer.StandardTransformerParameters.num_parallel)).

Use the [`ExtendableTransformer`](#components.transformer.ExtendableTransformer) class to represent a hypothetical transformer with an apparent power capacity that is flexible, in order to optimize its apparent power capacity ([`ExtendableTransformerStaticResults.s_nom_opt`](#components.transformer.ExtendableTransformerStaticResults.s_nom_opt)).

## API Reference

[`Transformer`](#components.transformer.Transformer) and [`ExtendableTransformer`](#components.transformer.ExtendableTransformer) both inherit from the [`BaseTransformer`](#components.transformer.BaseTransformer) parent class.

::: components.transformer
    options:
      inherited_members: false
      members_order: source
      show_labels: false
      show_root_toc_entry: false
      show_signature_annotations: true
      show_source: false
      members: ['CustomTransformerParameters', 'StandardTransformerParameters', 'BaseTransformer', 'Transformer', 'ExtendableTransformer', 'TransformerStaticResults', 'ExtendableTransformerStaticResults', 'TransformerDynamicResults']
