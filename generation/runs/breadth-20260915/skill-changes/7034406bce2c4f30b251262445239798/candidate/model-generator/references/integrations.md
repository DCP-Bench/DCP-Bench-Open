# Integrations: building one, and certifying one

Read this only when the integration you need is missing or unusable.

## When the integration you need does not exist

Read `skills/solver-setup/SKILL.md` and follow it yourself. It covers choosing an
openly available CPU-capable framework, writing `metadata.yaml`, `run.py`, a
`Dockerfile`, a modelling skill under `solvers/<id>/skills/<name>/`, and running
the full readiness checklist before the integration may be used.

Create the run and record the setup skill **before writing any integration
file**, so the record freezes the instructions that guided the work rather than
whatever they became afterwards:

```sh
python -m generation.manage setup-attempt --run <run-id> --solver SOLVER --skill skills/solver-setup
```

Doing it the other way round records the skill after the fact, which
proves nothing about what you followed. If you realise you have already started,
say so in the setup notes rather than letting the record imply otherwise.

Record `setup_finished`, `setup_blocked` or `interrupted` with
`generation.manage event`, including the evidence paths. Setup consumes the same
wall-clock budget. Allow at most one active repair per integration; when the
setup budget is spent, report the integration as blocked and pick a different
target. A setup that ends without a passing readiness record has failed, however
much was built.

### An integration that already exists but has no readiness record

An integration without a current `readiness.json` is reported as unusable by
`next_work`. That does not mean it is broken, and it must not be rebuilt.
Certify it instead — a one-time job per integration, and the same steps after
any change that invalidates an existing record:

1. Write `solvers/<id>/readiness_test.py` that drives the repository evaluator
   through the whole checklist — satisfaction, changed instances, malformed
   output, empty output, timeout cleanup, isolation, missing image, minimization,
   maximization, enumeration, plus `compilation_error` for a compiled
   integration — printing a JSON object of check name to Boolean and exiting
   nonzero if any failed.
   `solvers/cpmpy_python/readiness_test.py` is a working example to adapt; the required names are in `generation/AGENTS.md`.
2. Build the image if it is not present: `python -m evaluation.build <id>`.
3. Record readiness, which runs your script and keeps its output as evidence:

   ```sh
   python -m generation.readiness check --solver ID --output solvers/ID/readiness.json
   ```

The record binds the image identity and the hashes of `metadata.yaml`, `run.py`,
`Dockerfile` and the check script, so it must be redone whenever any of them
changes. The helper runs the checks rather than believing a summary — but it
cannot judge whether your script tests the right things. Write it to fail.
