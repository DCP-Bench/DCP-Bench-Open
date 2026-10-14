# Run protocol

## Configuration and artifact ownership

Create a unique UTC timestamp plus random-suffix run ID. Use exclusive creation
so two runs cannot share an attempt directory. Work one pair at a time; if a
second run is active in the same checkout, give it its own run ID. Never replace
an existing accepted artifact as an incidental effect of generation.

Use `generation.manage init`, `attempt`, `evaluate`, `retain`, `event`, and
`status` from the repository root; read repository `generation/AGENTS.md` for
exact interfaces and artifact schemas. These helpers own run/attempt manifests,
skill references, evaluation records, and accepted-model persistence. Do not
reimplement that logic through ad-hoc shell writes.

Use the attempt path returned by the helper. Add the problem brief and any
lessons with their evidence. Setup, skill-change and interruption events share
the same run ID. The evaluate helper preserves separate `candidate.<ext>` bytes
as the immutable evaluated submission, so the model file you wrote stays
readable alongside exactly what was checked.

The run configuration records actual agent, target policy and overall budgets;
the coordinator enforces them. On resume, `status` identifies stored outcomes.
Do not restart or overwrite a completed attempt; use unchanged preserved bytes
for an interrupted evaluation or allocate a fresh attempt for a repair. Keep
old evidence even if its acceptance is stale after an environment change.

## Evaluation

Normally use `generation.manage evaluate` to obtain and record the result.
The direct CLI below documents the underlying evaluator and can be used for
independent diagnosis; it does not replace the helper's own records for retention.
Run from the repository root using the installed evaluation environment. Existing
flags, rather than this document, are authoritative if the CLI has changed;
inspect `python -m evaluation.check --help` and record any adaptation.

Fast check (substitute the environment executable and real paths/IDs):

```sh
python -m evaluation.check generation/runs/RUN/attempts/PROBLEM/SOLVER/attempt-001/model.py --problem PROBLEM --solver SOLVER --instance-count 1 --solution-limit 1 --execution-timeout 60 --reference-timeout 60 --compilation-timeout 120 --memory-mb 2048 --cpus 1
```

Capture stdout as `evaluation.json` and stderr separately with the host's process
API, preserving exit code and actual invocation. A JSON result with
`accepted=true` and exit 0 is a pass; nonzero, missing, malformed, or inconsistent
results never pass. Do not treat empty stderr or successful compilation as a pass.

The command above is the minimum check. The recommended campaign profile is
`--instance-count 99 --solution-limit 2`, which covers every distinct instance a
problem has: a count above the available supply is honoured as a budget and
`instances_available` reports the real supply. `solution_limit` above 1 needs
`enumeration: true` in the integration's metadata, otherwise the result is
`unsupported_capability`.

Explicit IDs use `--instance-ids example json:2`; do not combine them with a
nondefault instance count, and note that a named ID which does not exist is an
error rather than a budget. Deduplication means not every JSON row has a
selectable ID. An empty instance list still permits the embedded example.

Retention checks the result against the run's frozen profile, so the profile is
the coverage claim. Do not lower it to convert a failure into a pass.

### Failure routing

Read top-level `reason`, `detail`, per-instance details, and `runner_status`.

| Result | Action |
| --- | --- |
| `invalid_solution`, `suboptimal_solution`, `no_solution` | A counterexample was found: repair model/declared outputs. Holds even when the run later timed out or crashed. |
| `invalid_output`, `output_limit`, `compilation_error` | Inspect diagnostics. Candidate syntax/API/protocol mistakes go to modeller; a failure reproducible with a known-good fixture goes to setup. Too few distinct solutions without an exhaustion status means the enumeration implementation is at fault. |
| `infrastructure_error` | Diagnose image/engine/dependency failure; bounded setup repair, then reevaluate the same candidate. |
| `unsupported_solver` | Resolve the integration ID or invoke bounded setup for the missing integration. |
| `unsupported_capability` | Check requested capability against integration; setup may implement/test it. Otherwise block this pair under this profile. |
| `invalid_request` | Correct coordinator paths/flags without changing the agreed coverage. A named instance ID that does not exist is a configuration blocker; a count above the available supply is not, and is honoured as a budget. |
| `reference_error`, `unsupported_unsat` | Record a reference blocker; do not repair reference data/code in this workflow. Continue other pairs. |
| `reference_timeout` | Inconclusive; use a recorded larger bound only if authorized by the run profile/budget, otherwise block. |
| `execution_timeout`, `memory_limit`, `execution_error` | Inconclusive: solutions checked before the failure were all accepted, so read `solutions_checked` before deciding. Inspect for a model-performance repair or integration failure. Count repairs toward attempts; do not loop indefinitely. A large `solution_limit` shares one execution budget, so raising it makes this outcome likelier. |
| Unknown reason, missing/truncated result, coordinator crash | Preserve raw evidence, diagnose once within budget, and block if unresolved. Never infer acceptance. |

Keep setup attempts separate from model attempts, but both consume wall-time and
any cost budget. A setup repair must pass its tests before the original candidate
is reevaluated. A deadline stops new work and requires
cleanup and a checkpoint even mid-attempt.

## Retain an accepted model

Use `python -m generation.manage retain --attempt ATTEMPT_PATH`. It verifies the
coordinator-produced evaluation, profile/IDs, actual coverage, candidate bytes
and the cited skill before creating an unused run/attempt child under
`generated_models/<problem_id>/<solver_id>/`. It preserves legacy artifacts.
Use the returned path in the final report. Do not edit retained bytes; a change
requires another evaluation. Skill proposals can remain pending independently.
