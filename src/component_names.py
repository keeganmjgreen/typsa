PLURAL_TO_SINGULAR_COMPONENT_NAMES = {
    "buses": "bus",
    "carriers": "carrier",
    "generators": "generator",
    "global_constraints": "global_constraint",
    "line_types": "line_type",
    "lines": "line",
    "links": "link",
    "loads": "load",
    "networks": "network",
    "shapes": "shape",
    "shunt_impedances": "shunt_impedance",
    "storage_units": "storage_unit",
    "stores": "store",
    "sub_networks": "sub_network",
    "transformer_types": "transformer_type",
    "transformers": "transformer",
}

SINGULAR_TO_PLURAL_COMPONENT_NAMES = {
    v: k for k, v in PLURAL_TO_SINGULAR_COMPONENT_NAMES.items()
}
