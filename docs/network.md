# Network

Like PyPSA, TyPSA provides a `Network` object.

`typsa.Network` is a drop-in replacement for `pypsa.Network`, providing identical functionality along with additional methods for adding TyPSA component objects and getting results. Under the hood, `typsa.Network` inherits from `pypsa.Network`. This allows you to switch to TyPSA in an existing project and try TyPSA out, without having to change all your code at once, because all your existing PyPSA-based code will function the same as before.

## API Reference

::: network
    options:
      inherited_members: false
      members_order: source
      show_bases: false
      show_labels: true
      show_root_toc_entry: false
      show_signature_annotations: true
      show_source: false
      members: ['Network']
