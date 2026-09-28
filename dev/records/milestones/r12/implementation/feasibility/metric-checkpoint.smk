"""P0 completed responses -> bounded plan -> exact ready metric path."""

verify_metric_plan()
if not Path("planning/metric.json").exists():
    print("P0_UNRESOLVED metric identity awaits response checkpoint", flush=True)


checkpoint plan_metrics:
    input:
        inventory="retained/inventory.json",
        native="hydrology/wflow/output.csv",
    output:
        "planning/metric.json",
    run:
        write_json(output[0], metric_plan())


def selected_metric(wc):
    plan = read_json(checkpoints.plan_metrics.get().output[0])
    return plan["target"]


def selected_response(wc):
    plan_path = checkpoints.plan_metrics.get().output[0]
    plan = read_json(plan_path)
    if wc.metric_id != plan["id"]:
        raise ValueError(f"MetricIdentityMismatch: {wc.metric_id}")
    if plan != metric_plan():
        raise ValueError("StaleMetricPlan: planning/metric.json")
    ready = Path(plan["target"])
    if ready.exists() and read_json(ready) != metric_publication(plan):
        raise ValueError(f"ImmutablePublicationMismatch: {ready}")
    return [str(plan_path), plan["response"]["artifact"]]


rule reduce_metric:
    input:
        selected_response,
    output:
        update("metrics/{metric_id}/metrics.json"),
    wildcard_constraints:
        metric_id="[a-f0-9]{64}",
    run:
        plan = read_json(input[0])
        preserve_json(output[0], metric_publication(plan))
