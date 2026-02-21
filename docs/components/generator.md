# Generator

Use the [`Generator`](#components.generator.Generator) class to represent a power generator with a given active power capacity ([`p_nom`](#components.generator.Generator.p_nom)), in order to optimize its active power over time ([`GeneratorDynamicResults.p`](#components.generator.GeneratorDynamicResults.p)).

Use the [`ExtendableGenerator`](#components.generator.ExtendableGenerator) class to represent a hypothetical generator with an active power capacity that is flexible, in order to also optimize the active power capacity ([`ExtendableGeneratorStaticResults.p_nom_opt`](#components.generator.ExtendableGeneratorStaticResults.p_nom_opt)).

Use the [`CommittableGenerator`](#components.generator.CommittableGenerator) class to represent a generator with unit commitment (start-up and shut-down) constraints, in order to also optimize when the generator is operating ([`CommittableGeneratorDynamicResults.status`](#components.generator.CommittableGeneratorDynamicResults.status)).

## API Reference

[`Generator`](#components.generator.Generator), [`ExtendableGenerator`](#components.generator.ExtendableGenerator), and [`CommittableGenerator`](#components.generator.CommittableGenerator) all inherit from the [`BaseGenerator`](#components.generator.BaseGenerator) parent class.

::: components.generator
    options:
      inherited_members: false
      members_order: source
      show_labels: false
      show_root_toc_entry: false
      show_signature_annotations: true
      show_source: false
      members: ['BaseGenerator', 'Generator', 'ExtendableGenerator', 'CommittableGenerator', 'ExtendableGeneratorStaticResults', 'GeneratorDynamicResults', 'CommittableGeneratorDynamicResults']
