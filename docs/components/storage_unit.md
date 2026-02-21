# Storage Unit

Use the [`StorageUnit`](#components.storage_unit.StorageUnit) class to represent a storage unit with a given active power capacity ([`p_nom`](#components.storage_unit.StorageUnit.p_nom)), in order to optimize its active power over time ([`StorageUnitDynamicResults.p`](#components.storage_unit.StorageUnitDynamicResults.p)). The storage unit's energy capacity is determined by its [`max_hours`](#components.storage_unit.BaseStorageUnit.max_hours) in conjunction with [`p_nom`](#components.storage_unit.StorageUnit.p_nom).

Use the [`ExtendableStorageUnit`](#components.storage_unit.ExtendableStorageUnit) class to represent a hypothetical storage unit with an active power capacity that is flexible, in order to also optimize the active power capacity ([`ExtendableStorageUnitStaticResults.p_nom_opt`](#components.storage_unit.ExtendableStorageUnitStaticResults.p_nom_opt)).

## API Reference

[`StorageUnit`](#components.storage_unit.StorageUnit) and [`ExtendableStorageUnit`](#components.storage_unit.ExtendableStorageUnit) both inherit from the [`BaseStorageUnit`](#components.storage_unit.BaseStorageUnit) parent class.

::: components.storage_unit
    options:
      inherited_members: false
      members_order: source
      show_labels: false
      show_root_toc_entry: false
      show_signature_annotations: true
      show_source: false
      members: ['BaseStorageUnit', 'StorageUnit', 'ExtendableStorageUnit', 'ExtendableStorageUnitStaticResults', 'StorageUnitDynamicResults']
