"""P0 retained-response preflight with no simulation producer definitions."""

validate_inventory()

rule metrics:
    input:
        ready=lambda wc: selected_metric(wc),
    default_target: True
