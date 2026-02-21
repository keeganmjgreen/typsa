# Store

Use the [`Store`](#components.store.Store) class to represent an energy store with unlimited power capacity and given energy capacity ([`e_nom`](#components.store.Store.e_nom)), in order to optimize its active power over time ([`StoreDynamicResults.p`](#components.store.StoreDynamicResults.p)).

Use the [`ExtendableStore`](#components.store.ExtendableStore) class to represent a hypothetical store with an energy capacity that is flexible, in order to also optimize the energy capacity ([`ExtendableStoreStaticResults.e_nom_opt`](#components.store.ExtendableStoreStaticResults.e_nom_opt)).

## API Reference

[`Store`](#components.store.Store) and [`ExtendableStore`](#components.store.ExtendableStore) both inherit from the [`BaseStore`](#components.store.BaseStore) parent class.

::: components.store
    options:
      inherited_members: false
      members_order: source
      show_labels: false
      show_root_toc_entry: false
      show_signature_annotations: true
      show_source: false
      members: ['BaseStore', 'Store', 'ExtendableStore', 'ExtendableStoreStaticResults', 'StoreDynamicResults']
