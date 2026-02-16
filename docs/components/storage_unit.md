# Storage Unit

Use the `StorageUnit` class to represent a storage unit with a given active power capacity (`p_nom`), in order to optimize its active power over time (`StorageUnitDynamicResults.p`). The storage unit's energy capacity is determined by its `max_hours` in conjunction with `p_nom`.

Use the `ExtendableStorageUnit` class to represent a hypothetical storage unit with an active power capacity that is flexible, in order to also optimize the active power capacity (`StorageUnitStaticResults.p_nom_opt`).

## API Reference

`StorageUnit` and `ExtendableStorageUnit` both inherit from the `BaseStorageUnit` parent class.

::: components.storage_unit
    options:
      inherited_members: false
      members_order: source
      show_labels: false
      show_root_toc_entry: false
      show_signature_annotations: true
      show_source: false
      members: ['BaseStorageUnit', 'StorageUnit', 'ExtendableStorageUnit', 'StorageUnitStaticResults', 'StorageUnitDynamicResults']
