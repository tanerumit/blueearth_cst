"""P0 stage-2 producers; no source-generation rules are admitted here."""

rule all:
    input:
        ready=lambda wc: selected_metric(wc),
    default_target: True

rule simulate_response:
    output:
        "hydrology/wflow/output.csv",
    run:
        Path(output[0]).write_text("q\n1\n", encoding="utf-8")

rule inventory_response:
    input:
        "hydrology/wflow/output.csv",
    output:
        "retained/inventory.json",
    run:
        write_json(output[0], {
            "artifact": str(input[0]), "variables": ["q"],
            "sha256": file_digest(input[0]),
        })
