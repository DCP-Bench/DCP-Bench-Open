# Model evaluation

Runs a submitted model inside a locked-down container and checks its declared
outputs against a CPMpy reference whose optimum has been proven independently.

## What acceptance means

Evaluation looks for a **counterexample**: a solution of the submitted model
that the reference does not accept. `solution_limit` is the budget for that
search, not a requirement — a higher limit is a stronger test, never a stricter
pass bar. Exhausting the submitted model before reaching the limit is a pass.

`accepted=true` therefore means no counterexample was found within budget,
against the reference's **declared outputs** — not that the model is equivalent
to the reference. An overconstrained model can pass, because being too strict
leaves no trace in the outputs examined; a submission with no solutions at all
is the one exception and always fails. Some references declare only an
objective value. Reference UNSAT is unsupported in v1.

`tolerate_inconclusive` relaxes coverage without relaxing soundness: an instance
that only times out (`reference_timeout` or `execution_timeout`) is recorded in
`skipped_instances` and the remaining instances are still checked, and
acceptance then needs at least one instance verified — `no_instance_verified`
otherwise. A solution the reference rejects still fails the whole evaluation
immediately, tolerated or not.

Solutions are checked before the runner's exit status is consulted, so a
rejected solution is a rejection even when the run later timed out or crashed.
`reason` separates model rejection (`invalid_solution`, `suboptimal_solution`,
`no_solution`) from inconclusive runs (`reference_timeout`,
`execution_timeout`, `execution_error`), protocol violations (`invalid_output`, `output_limit`)
and infrastructure failure (`infrastructure_error`).

## Setup

Python 3.12, `requirements.txt`, and a running Docker Linux engine. Images
target linux/amd64 and pin their solver versions. Build them explicitly —
`evaluate()` never builds or installs anything:

```sh
python -m evaluation.build                      # all six, or name specific ids
python -m evaluation.check examples/abbots.py --problem abbots_puzzle --solver cpmpy_python
python -m evaluation.check examples/abbots.py --problem abbots_puzzle --solver cpmpy_python --solution-limit 2
```

The CLI prints one JSON result and exits 0 on acceptance, 1 otherwise. The
Python API is `from evaluation import evaluate`. Call it under an
`if __name__ == "__main__":` guard — reference checks spawn a child process.

Select instances with `--instance-count 3` or `--instance-ids example json:1`.
IDs are original JSON indices; an instance identical to an earlier one has no
ID of its own. Identity uses only the reference's declared data fields; names
and notes do not increase coverage. The first distinct record retains its
metadata. A count is a budget like `solution_limit`: asking for more instances
than exist checks every one that exists, and `instances_available` reports the
supply. A named `--instance-ids` that does not exist is still an error.

| Limit | Default | Flag |
| --- | --- | --- |
| Execution, per instance | 60 s | `--execution-timeout` |
| Reference operation | 60 s | `--reference-timeout` |
| C++ compilation | 120 s | `--compilation-timeout` |
| Memory | 2048 MiB | `--memory-mb` |
| CPUs | 1 | `--cpus` |

Candidate wall-clock adds a 10 s container-startup allowance; solver time is
limited separately inside the runner. Reference time covers process startup
plus each check, and a check may need both a feasibility and an optimality
solve. Output is capped at 8 MiB per stream and container scratch at 512 MiB.

Results carry per-instance outcomes, `instances_available`,
`unperformed_instances`, `skipped_instances`, limits, timings, model/reference/instance hashes, and
the image digest actually executed.
Evaluation stops at the first failure, so `instances_checked` counts only
passes — inspect `instances` for the one that failed. Wall time includes
startup and compilation, so it is not comparable to the runner's
`solve_seconds`.

## Submitting a model

Pick an integration: `cpmpy_python`, `ortools_cp_sat_python`,
`ortools_cp_sat_cpp`, `minizinc_gecode`, `z3_python` or `clingo_asp`. Read its
modelling skill first, at `solvers/<id>/skills/<name>/SKILL.md`. Each
`solvers/<id>/` holds `metadata.yaml`, `run.py`, a `Dockerfile`, the
`readiness_test.py` that certifies it, and that skill.

Models are instance-agnostic. Python implements `build(instance)`, C++
implements `Build(instance, model, outputs)`, MiniZinc declares matching data
parameters and emits JSON, and an ASP program reads facts and shows atoms.
Working examples live in `tests/fixtures/`.

Only the entrypoint file is copied into the container; its parent directory is
never mounted. v1 accepts one file.

## Runner protocol

The image entrypoint receives `/input/model.<ext>` and `/input/request.json`
(`instance`, `solution_limit`, `execution_timeout`, `compilation_timeout`,
`legacy`, `outputs`) and writes JSONL to stdout, logs to stderr. `outputs` lists
the reference's declared output names, for a runner whose language cannot use
them verbatim — an ASP predicate cannot start with a capital, so `clingo_asp`
maps each key to the predicate with its first character lowered. The names are
already in the brief a modeller works from, and no solution is ever included:

```json
{"type":"solution","values":{"x":0,"y":2}}
{"type":"status","status":"limit","solve_seconds":0.01}
```

Solution records are followed by exactly one status.

| Status | Meaning |
| --- | --- |
| `limit` | requested solution count reached |
| `complete` | enumeration exhausted |
| `timeout` | budget spent, or optimum unproven |
| `unsat` | no solution exists |
| `error` / `unsupported` / `compilation_error` | see `detail` |

Zero solutions never pass. Returning fewer than N distinct solutions requires
`complete`, which is the runner's report that the *submitted* model has no more
— it is not read as a claim about the reference. Anything less from a runner
that neither reached the count nor reported exhaustion is `invalid_output`.
Optimization runners emit only final optimal outputs; the evaluator re-derives
optimality itself and never trusts a claimed objective.

## Adding an integration

Add a `solvers/<id>/` directory implementing the protocol, plus smoke tests.
The evaluator dispatches on integration ID, never on language name. Metadata
declares `id`, `image`, `extension`, `enumeration`, descriptive
language/framework/solver fields, and optionally `compilation: true` to
allocate the separate compilation budget. Installation belongs in the
Dockerfile. Shared container code lives in `runner/`, which every image copies;
`runner/requirements.txt` pins the Python solver stack.

Containers run with no network, a read-only root, an unprivileged user, no
added capabilities, `no-new-privileges`, and memory/CPU/PID caps. Reference
checking happens in a separate trusted host process the container never sees.

A future problem-specific converter must run inside this same container, with
every staged file in the artifact hash — never on the host, and never by
mounting a submission directory.

## The reference loader

References are trusted dataset scripts. The loader parses the AST, substitutes
instance values for the marked `# Data` section, and drops the solve/output
tail — that tail never executes. Declared outputs are mapped back to reference
expressions and bound with CPMpy equality constraints, never by running
candidate-generated Python.

Exact keys and array shapes are required. Integer outputs need JSON integers;
Boolean outputs accept JSON Booleans or 0/1. Auxiliary variables are completed
by the reference solver. Instances must supply every data-section field; extra
`name`/`note` metadata keys are ignored.

## Legacy compatibility

`eval.py` (JSONL CLI, JSON to `summary.txt`) and `verify_models.py`
(single-model CLI with badge sidecars) both route through this package. Legacy
framework names map onto integrations (CPMpy, OR-Tools, MiniZinc); anything
else fails explicitly rather than running as arbitrary host Python. Legacy
programs get the embedded example and one solution only. Stored results are
not bulk migrated or reverified.

## Validation

```sh
python -W ignore::SyntaxWarning -m unittest tests.test_evaluation -v
```

The dataset audit runs every time: all references must load, the first instance
entry must equal the embedded example exactly, every listed instance must build
the reference, and only `name`/`note` extra keys are permitted.

Two checks are opt-in:

```sh
DCP_CONTAINER_TESTS=1 python -m unittest tests.test_solvers -v   # needs built images
DCP_UNSAT_AUDIT=1 python -m unittest tests.test_evaluation.ReferenceTests.test_no_unsat_instances
```

Skipped container tests are not evidence of end-to-end success: the container
run is the authoritative one.

Dataset changes and the reasoning behind them are recorded in
[SOURCES.md](../SOURCES.md).
