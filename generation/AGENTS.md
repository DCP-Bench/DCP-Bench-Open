# Operating the generation helpers

The contract an agent works to. `generation/README.md` is the short human
overview; this file is the exact syntax, schemas and rules.

`skills/model-generator` runs the campaign loop; `skills/solver-setup` creates or
repairs integrations. One agent reads them and does the work. These Python
commands provide records and checks; they do not choose a solver, call an LLM
provider, or replace the skills.
Use the repository Python environment from the repository root. All operations
are local; nothing installs skills globally or publishes results.

## What work remains

```sh
python -m generation.next_work [--limit N] [--include-unready]
```

Reports every integration with whether it is usable, the problem count, how many
pairs already have a current-format accepted model, and the next candidate pairs.
Only current evidence counts: a pair is covered when
`generated_models/PROBLEM/SOLVER/*/record.json` was written by this evaluator and accepted.
Legacy directories are counted separately and are never coverage. An integration
without a current readiness record is reported with its blocker and contributes
no eligible pairs unless `--include-unready` is given.

`generation/blockers.json` lists pairs not worth attempting again. Each entry
carries `problem`, `solver` (null for every integration, right when the limit is
in the reference), `reason`, `detail`, `evidence` and `recorded`. `next_work`
withholds them from the queue and reports them under `blocked_pairs`; a
malformed or missing file is ignored rather than emptying the queue.

## Model attempts

```sh
python -m generation.manage init --run RUN --config config.json
python -m generation.manage setup-attempt --run RUN --solver SOLVER --skill skills/solver-setup
python -m generation.manage attempt --run RUN --problem abbots_puzzle --solver SOLVER --skill skills/SKILL
python -m generation.manage evaluate --attempt ATTEMPT_PATH --model MODEL_PATH
python -m generation.manage retain --attempt ATTEMPT_PATH
python -m generation.manage status --run RUN
python -m generation.manage event --run RUN --kind setup_started --data '{"solver_id":"SOLVER","evidence":"PATH"}'
```

`--config` is optional. Its object can contain `agent`, `budgets`, and `profile`.
The profile uses `evaluate()` keyword names: `instance_count`, `instance_ids`,
`solution_limit`, `execution_timeout`, `reference_timeout`, `compilation_timeout`,
`memory_mb`, and `cpus`. Choose count or IDs. Defaults are one instance/solution,
60-second execution/reference bounds, 120-second compilation, 2048 MiB, one CPU.
The coordinator enforces overall run/attempt budgets recorded in config; the
evaluator enforces individual solve limits. Helpers do not enforce LLM cost caps.

Use the path returned by `attempt` rather than constructing it. Attempts live
under `generation/runs/RUN/attempts/PROBLEM/SOLVER/attempt-NNN/`. They contain the
candidate, evaluation and retention pointer, and a reference to the solver
skill: its path, the commit it ran against, and a hash of its bytes. Add `prompt.md`, `response.md`, and `lessons.md` as appropriate.
Setup work lives under the same run's `setup/SOLVER/ATTEMPT/`; record started,
finished, blocked and interrupted events with command logs and skill hashes.
Give a second concurrent run its own run ID rather than writing to the same
pair. JSONL events describe work; they cannot authorize acceptance.

## What a finished run keeps

While a run is live it holds everything a resume needs. Once it is finished it
is trimmed to the ledger and the verdicts:
`run.json`, `events.jsonl`, and per attempt `attempt.json`, `evaluation.json`,
`retained.json` and the model itself. Dropped are the `candidate.*` duplicates of
the model, the generated `brief.md`, and the readiness copy. Accepted models keep their permanent
home under `generated_models/`; what the ledger adds is the attempts that
failed.

The run manifest and per-attempt profiles are frozen. Resume using `status` and
preserved artifacts; changing a profile creates a new run, so choose a
thorough profile up front — `instance_count: 99` covers every distinct instance
a problem has, and a wrong model still fails on an early one. Historical/legacy directories are not overwritten. Retained artifacts
live in a unique run/attempt child beneath `generated_models/PROBLEM/SOLVER/`.

## Integration readiness

Every integration ships `solvers/<id>/readiness_test.py`, a required artifact
alongside the runner and Dockerfile. It drives the evaluator against the built
image, prints a JSON object mapping check name to Boolean on stdout, and exits
nonzero if any check failed. `generation.readiness check` runs it, keeps its
stdout and stderr as evidence, and records the result only on a clean exit with
every required check true.

It must cover **every** required test:
`satisfaction`, `changed_instances`, `malformed_output`, `empty_output`,
`timeout_cleanup`, `isolation`, `missing_image`; plus `minimization` and
`maximization` (or `unsupported_optimization` if metadata explicitly sets
`optimization:false`), `enumeration` (or `unsupported_enumeration`), and
`compilation_error` for compiled integrations. Named checks must match actual
test assertions in the evidence; the coordinator is responsible for that
assessment. The helper prevents omission/stale evidence, not falsified reports.

```sh
python -m generation.readiness check --solver ID --output solvers/ID/readiness.json
python -m generation.readiness verify --solver ID --record solvers/ID/readiness.json
```

`--evidence-dir` puts the captured output somewhere other than beside the record.
`--report REPORT.json` skips execution and accepts a report you supply, for an
integration whose checks genuinely cannot run from one script; prefer the script.

The record binds actual image identity and the hashes of `metadata.yaml`,
`run.py`, `Dockerfile` and `readiness_test.py`, plus the evidence hashes, so
editing any of them invalidates it. Attempt creation, evaluation, and retention
verify it. Evidence paths are stored relative to the repository, so a record verifies on
any checkout. Keep the evidence files available. A changed integration needs
fresh tests and a new record; archive the old one before replacing its canonical
path.

## Skill provenance and improvement (all skill levels)

```sh
python -m generation.skills validate skills/model-generator --project
python -m generation.skills propose --run RUN --skill skills/model-generator --candidate working/model-generator --evidence "Failure cause and run evidence path"
python -m generation.skills check PROPOSAL_PATH --checks trusted-checks.json
python -m generation.skills apply PROPOSAL_PATH
```

Each skill bundle carries a plain `sources.md` listing the documentation its
instructions came from. `validate --project` requires that file plus a valid
behavioural eval manifest. An attempt records the skill by reference, not by copy: its path, the commit it
ran against, whether that path had uncommitted changes, and a hash of its bytes.
Evaluation and retention re-hash the live bundle, so editing a skill mid-attempt
is refused. That record is what ties a model to the skill version behind it.

`trusted-checks.json` is a nonempty list such as:

```json
[{"argv": ["python", "tests/my_skill_regression.py", "{skill}"], "timeout": 60}]
```

The coordinator owns this harness outside the editable candidate. Commands run
against both frozen old and proposed bundles; `{skill}` is replaced by each
bundle path. They must test the affected behaviour or API example. A blanket
exit-zero command or format-only validator does not substantiate a behavioural
improvement. Commands execute trusted test code on the host; generated solver
models still execute only through the container evaluator. Capture all outputs.

Only all-passing candidate checks allow application. A changed canonical skill,
candidate, or recorded validation result prevents applying stale evidence.
Propose/check/apply emit shared `skill_proposed`, `skill_checked`, and
`skill_applied` events. Applied changes retain the previous bundle for rollback. Every subsequent
attempt records the skill afresh; existing attempts never adopt edits retroactively.
Tests executed by these helpers are evidence, not an adversarial security
boundary against another process with write access to the repository.

## Behavioural evaluations

The skill bundles contain `evals/evals.json` with prompts and observable
assertions. They are specifications, not stored pass claims.

```sh
python -m generation.behaviour prepare --skill skills/model-generator --case empty-solvers --output TRIAL_DIRECTORY
python -m generation.behaviour assess TRIAL_DIRECTORY --assessment assessment.json
```

Prepare freezes the skill and writes `prompt.md`. Give that prompt to a fresh
agent session with a bounded budget and an isolated checkout prepared with the
stated prerequisites. Do not provide the expected
solution or ask it to copy existing integration directories. Retain a trace,
commands and artifacts. An independent assessor reads the original assertions
and actual outputs, then supplies:

```json
{
  "assessor": "independent-agent-or-reviewer",
  "execution": "actual worker/run identifier",
  "assertions": {
    "ASSERTION_ID": {
      "passed": true,
      "observation": "Concrete observed result and its limitation",
      "evidence": ["absolute/path/to/actual/result.json"]
    }
  }
}
```

Every assertion must be assessed; missing execution/evidence cannot pass. The
assessor, not this recorder, judges semantic behaviour. The recorder verifies
all evidence files exist, hashes them, checks the cited skill stayed unchanged,
and reports success only if all explicit assertions pass. Keep failed trials
too. Never present a prepared or skipped case as executed. Standard unit tests
exercise bookkeeping and update rejection; they do not replace agent trials.
