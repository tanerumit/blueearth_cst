# Executed bounded verification

Run from the worktree root before the final re-score. All final checks passed;
`check-before.log` records the expected missing-implementation failure before
the reducer was created. `mutation.log` records a real source mutation rejected
by the final boundary checker. The runner retains the disposable mutant in
the named scratch output; its exact construction is in `run-mutation.py`.

```powershell
$Assessment = 'dev/milestones/r12/implementation/evidence/gf15-accuracy-3x'
$StagePython = '.tmp/scratchpad/2026-09-11_0010/gf15-lmoments-readiness/venv/Scripts/python.exe'
$Scratch = '.tmp/scratchpad/2026-09-11_0010/gf15-accuracy-3x'
& $StagePython -B "$Assessment/check-rescore.py" *> "$Scratch/boundary.log"
Copy-Item "$Scratch/boundary.log" "$Assessment/verification/boundary.log"
& $StagePython -B "$Assessment/verification/run-mutation.py" --output "$Scratch/mutation-final" *> "$Assessment/verification/mutation.log"
& .pixi/envs/default/python.exe -m ruff check "$Assessment/rescore.py" "$Assessment/check-rescore.py" "$Assessment/verification/run-mutation.py" *> "$Assessment/verification/lint.log"
& .pixi/envs/default/python.exe -m ruff format --check "$Assessment/rescore.py" "$Assessment/check-rescore.py" "$Assessment/verification/run-mutation.py" *> "$Assessment/verification/format.log"
& $StagePython -B -c "from pathlib import Path; paths=list(Path('dev/milestones/r12/implementation/evidence/gf15-accuracy-3x').rglob('*.py')); [compile(p.read_text(encoding='utf-8'), str(p), 'exec') for p in paths]; print('PASS: in-memory compilation of', len(paths), 'Python sources')" *> "$Assessment/verification/compile.log"
```

Use fresh scratch directories/log filenames for reproduction. Do not overwrite
this frozen verification evidence. The final re-score command is in the
scientific handoff; its transcript is retained by the parent integration envelope.
