# Historical WF3 preparation cost — 2026-08-15

Measurements describe tree `e197502`, before the later workflow separation and execution redesign.
Condensed on 2026-10-20 without rerunning the benchmark. Full source:

```text
git show 53d07f52:dev/records/reviews/wf3-scenario-generation-trace-2026-08-15/trace.md
```

The source's section 3 transcribes
`test_case/test_rapid/benchmarks/wf3_benchmarks_experiment_rapid.md`.
That run used `project_config_rapid.yml`, a 384-cell fixture, two realizations and four perturbed
members plus one baseline per realization: ten simulation members, with three concurrent cores.
The recorded aggregate is **summed job duration, not elapsed wall time**.

| Historical operation | Jobs | Job-duration sum | Share | Largest job RSS |
|---|---:|---:|---:|---:|
| Prepare stress grid | 1 | 2.6 s | 0.2% | 96 MB |
| Generate baseline realizations | 1 | 34.7 s | 2.6% | 457 MB |
| Perturb realizations | 8 | 152.2 s | 11.5% | 407 MB |
| Write climate catalog | 1 | 9.2 s | 0.7% | 319 MB |
| Downscale realizations | 10 | 304.9 s | 23.0% | 303 MB |
| Run Wflow | 5 batches | 813.3 s | 61.2% | 912 MB |
| Derive indicators | 1 | 9.1 s | 0.7% | 257 MB |
| Other measured checks/configuration | — | About 2.5 s | — | — |
| Total measured work | — | About 1329 s | — | — |

Per-job perturbation durations were 18.9–19.2 s, downscaling 27.6–31.2 s and Wflow
batches 148.6–166.8 s. Approximate loads reported were 92%, 45% and 82%, respectively.
The source reports generation/catalog/indicator loads of 41%/57%/55%.
These are historical benchmark fields, not a calibrated hardware-utilization comparison.

Perturbation plus downscaling accounted for about 34.5% of summed measured job duration.
Both materialized intermediate NetCDFs later removed by the historical `temp()` chain.
This identifies a preparation cost; it does not measure how much an alternative implementation
would save. No on-the-fly alternative was benchmarked.

Three shared producers—region, spatial units and historical climate extraction—were already up to
date from WF1 and did not execute. Fresh standalone preparation would include those costs.
Config snapshot, metadata writing and gathers had no benchmark declarations; absent entries are
not measured zeros. Concurrent execution makes wall time lower than the summed duration.

The source's extrapolation to 34 members was a linear scaling estimate, not another observation.
Its suggestion that model simulation would occupy a larger share on a larger basin was untested.
The 912 MB batch peak does not isolate forcing residency or demonstrate a present-day batching limit.
These figures support investigation of this historical rapid case, not current production sizing.
