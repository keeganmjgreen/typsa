# Store

Use the `Store` class to represent an energy store with unlimited power capacity and given energy capacity (`e_nom`), in order to optimize its active power over time (`StoreDynamicResults.p`).

Use the `ExtendableStore` class to represent a hypothetical store with an energy capacity that is flexible, in order to also optimize the energy capacity (`ExtendableStoreStaticResults.e_nom_opt`).

## API Reference

`Store` and `ExtendableStore` both inherit from the `BaseStore` parent class.

::: components.store
    options:
      inherited_members: false
      members_order: source
      show_labels: false
      show_root_toc_entry: false
      show_signature_annotations: true
      show_source: false
      members: ['BaseStore', 'Store', 'ExtendableStore', 'ExtendableStoreStaticResults', 'StoreDynamicResults']
