---
title: "Indicator extension and local-set appendix"
format: html
---

The [independent module README](../../blueearth_cst/indicators/README.md) is the canonical extension
contract. It covers plain Python calls, trusted registration, response/context/result objects, closed
parameters, paired inputs, diagnostic tables, independent checkers and calculation identity.
WF4 owns input selection, warm-up handling, file publication and reuse guards.

## Canonical sources

The complete manual includes the sources below in this order.
They remain maintained beside their implementations; the publication uses those sources directly.
The [source declaration](local-source-appendix.yml) identifies their canonical locations.

| Appendix anchor | Maintained source |
|---|---|
| `indicator-module` | [Module README](../../blueearth_cst/indicators/README.md) |
| `indicator-default` | [Default](../../blueearth_cst/indicators/sets/default/README.md) |
| `indicator-flow-regime` | [Flow regime](../../blueearth_cst/indicators/sets/flow_regime/README.md) |
| `indicator-eflow-erfa` | [ERFA](../../blueearth_cst/indicators/sets/eflow_erfa/README.md) |
| `indicator-crop-water` | [Crop-water](../../blueearth_cst/indicators/sets/crop_water/README.md) |
| `indicator-flood-risk` | [Flood hazards](../../blueearth_cst/indicators/sets/flood_risk/README.md) |

Each set retains its formulas, units, missingness and qualification limits beside its implementation.
The crop-water appendix includes its complete preparation contract, including historical Qcrit.
No central rewrite of those rules is authoritative.

## Evidence availability

The ERFA R-oracle provenance and tests are repository evidence outside the promised offline appendix.
The declaration labels them as external to that assembly. Upstream literature and software manuals also
remain external references. Their links do not imply that an offline manual ships their contents.
Including calculation documentation establishes documented behavior, not new ecological, agricultural
or flood-risk qualification. Source checks and software tests do not establish basin-model adequacy.

## Extension boundary

Add installed trusted code using the module README's contract. YAML chooses it; YAML cannot import a path.
An unrelated set change does not enter a selected calculation's identity, while shared contributing source
changes do. Keep numerical expectations independent of production arithmetic. A new group policy requires
explicit review. The manuscript/scientific-method scope remains in the existing scientific approach.
