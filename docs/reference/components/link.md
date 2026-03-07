# Link

Use the [`Link`](#components.link.Link) class to represent a power link with a given active power capacity ([`p_nom`](#components.link.Link.p_nom)), in order to optimize its active power over time ([`LinkOptimizationDynamicResults.p0`](#components.link.LinkBaseDynamicResults.p0) or [`LinkOptimizationDynamicResults.p1`](#components.link.LinkBaseDynamicResults.p1)).

Use the [`ExtendableLink`](#components.link.ExtendableLink) class to represent a hypothetical link with an active power capacity that is flexible, in order to also optimize the active power capacity ([`ExtendableLinkOptimizationStaticResults.p_nom_opt`](#components.link.ExtendableLinkOptimizationStaticResults.p_nom_opt)).

Use the [`CommittableLink`](#components.link.CommittableLink) class to represent a link with unit commitment (start-up and shut-down) constraints, in order to also optimize when the link is operating ([`CommittableLinkOptimizationDynamicResults.status`](#components.link.CommittableLinkOptimizationDynamicResults.status)).

## API Reference

[`Link`](#components.link.Link), [`ExtendableLink`](#components.link.ExtendableLink), and [`CommittableLink`](#components.link.CommittableLink) all inherit from the [`BaseLink`](#components.link.BaseLink) parent class.

::: components.link
    options:
      inherited_members: false
      members_order: source
      show_labels: false
      show_root_toc_entry: false
      show_signature_annotations: true
      show_source: false
      members:
        - BaseLink
        - Link
        - ExtendableLink
        - CommittableLink
        - ExtendableLinkOptimizationStaticResults
        - LinkBaseDynamicResults
        - LinkOptimizationDynamicResults
        - CommittableLinkOptimizationDynamicResults
        - LinkPfDynamicResults
        - LinkNonlinearPfDynamicResults
