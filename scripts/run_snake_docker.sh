#!/bin/bash
set -euo pipefail
workflow_image="cst-workflow:0.0.1"
docker_root='/root/work'
docker run --rm --entrypoint='' \
    -v "$(pwd):${docker_root}" \
    -v /mnt/p/wflow_global/hydromt:/mnt/p/wflow_global/hydromt \
    -w "${docker_root}" \
    "${workflow_image}" \
    python scripts/run_workflows.py \
    --config test_case/project_config_baseline_linux.yml --cores 4 "$@"
