# Link

Use the `Link` class to represent a power link with a given active power capacity (`p_nom`), in order to optimize its active power over time (`LinkDynamicResults.p0` or `LinkDynamicResults.p1`).

Use the `ExtendableLink` class to represent a hypothetical link with an active power capacity that is flexible, in order to also optimize the active power capacity (`ExtendableLinkStaticResults.p_nom_opt`).

Use the `CommittableLink` class to represent a link with unit commitment (start-up and shut-down) constraints, in order to also optimize when the link is operating (`CommittableLinkDynamicResults.status`).

## API Reference

`Link`, `ExtendableLink`, and `CommittableLink` all inherit from the `BaseLink` parent class.

::: components.link
    options:
      inherited_members: false
      members_order: source
      show_labels: false
      show_root_toc_entry: false
      show_signature_annotations: true
      show_source: false
      members: ['BaseLink', 'Link', 'ExtendableLink', 'CommittableLink', 'LinkStaticResults', 'LinkDynamicResults', 'CommittableLinkDynamicResults']
