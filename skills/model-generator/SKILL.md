---
name: model-generator
description: Populate DCP-Bench Open with constraint models that the repository evaluator has accepted. Pick an uncovered problem and solver integration, write an instance-agnostic model, verify it against the reference, keep it, and move to the next one. Use for model generation campaigns, including building a solver integration that does not exist yet.
---

# Model generator

Add models to this repository that a real evaluator has accepted. One pair at a
time: choose a problem and a solver integration, write a model, prove it holds
up, commit it, move on.

You need this repository, its Python environment, and a running Docker Linux
engine. Building a new integration also needs network access for documentation.

## Read this part first: there is no recursion

Three kinds of skill exist here, and only three:

| Skill | How many | When you read it |
| --- | --- | --- |
| `skills/model-generator` — this file | one | now, as the campaign loop |
| `skills/solver-setup` | one | only when the integration you need does not exist |
| `solvers/<id>/skills/<name>` | one per integration | every time you write a model |

**You are the only agent.** You are the coordinator and the modeller. Nothing
here spawns another agent, and "invoke a skill" only ever means "read that file
and follow it". The third kind is the only one this workflow creates or edits;
this file and `solver-setup` change only through the procedure in
[operations](references/operations.md).

If you ever feel you need a fourth kind of skill, or a skill that writes a skill
that writes a skill, stop: that is a sign the work belongs in one of these three
or in a `generation/` helper.

## Before writing anything

1. **Create a new branch for this run, off whatever branch you are on now, and
   work only there.** Already being on a branch that is not `main` does **not**
   satisfy this: the run gets a branch of its own so its commits can be
   reviewed, kept or dropped as one unit, without disturbing the work the
   current branch already carries.

   ```sh
   git switch -c models/<run-id>
   ```

   Use the same `<run-id>` for `generation.manage init` below, so the branch and
   the run directory name each other. Do this before creating the run or
   touching any file. Never commit to `main`, and never push — the user does
   that. If the checkout has uncommitted work, stop and ask rather than
   absorbing it into your run or discarding it.
2. Read `AGENTS.md` and `evaluation/README.md`. Understand what acceptance means
   before you rely on it: the evaluator hunts for a solution the reference
   rejects, so a pass means no counterexample was found within the budget you
   asked for. A bigger budget is a stronger test, never a stricter pass bar.
3. Use the repository environment: `.venv/Scripts/python.exe` on Windows,
   `.venv/bin/python` on Unix when present. Run every command from the
   repository root. All paths below are relative to that root, not to wherever
   this skill is installed.
4. Confirm Docker is up. An unavailable engine is a blocker to report, not
   something to work around: candidate code never runs on the host.
5. Agree the budget before generating. Defaults, unless the user says otherwise:
   **10 model attempts per pair**, **one new integration per run**, **two setup
   attempts per integration**, **60 minutes total**. Stop starting new work when
   the budget is gone, then checkpoint what exists.

## Pick the work

```sh
python -m generation.next_work
```

This lists every integration with whether it is usable, which pairs still have
no accepted model, and the first candidates to take. Take `next_pairs[0]` and
work down: the list already leads with problems that have several instances,
where a model that hardcoded the example cannot pass.

**Which integration.** Use the one the user named. With no preference, deepen a
ready integration rather than adding a framework — there is far more uncovered
work than there are frameworks. Build a new one when the user asks for a
framework by name, when nothing ready has eligible work left, or when `solvers/`
is empty. Choosing it yourself means an openly available, CPU-only framework
with documentation you can actually reach, and a recorded reason. An empty
`solvers/` means the work has not started, never that it is finished.

**The first pair on a new integration** is a confidence check, not a coverage
grab: take a small problem with several instances, so a mistake shows up as a
model failure rather than as a mystery about infrastructure you just built.
`csplib_054_n_queens` suits this. Then work the queue normally.

An integration reported as not `ready` cannot be used at all — certify, build or
repair it first (see below). Legacy directories under `generated_models/` are
**not** coverage: they predate this evaluator and were never checked by it.

`generation/blockers.json` records pairs not worth attempting again — usually a
reference no bound we have tried can solve. `next_work` withholds them and lists
them under `blocked_pairs`. Do not retry one without new information, and add an
entry, with its evidence, whenever you block a pair yourself. A blocker with a
null solver applies to every integration, which is right when the limit is in
the reference.

## Set the run profile so a pass means something

Create the run once, on the branch you made above and using that same run ID,
with a profile chosen to be thorough rather than quick:

```sh
python -m generation.manage init --run <run-id> --config config.json
```

`config.json` holds the agent identity, the budgets you agreed, and the profile.
Write it **inside the repository** — the helper refuses a path outside it:

```json
{
  "agent": "whatever identifies you, recorded with every attempt",
  "budgets": {"integrations": 1, "setup_attempts_per_integration": 2,
              "model_attempts_per_pair": 10, "wall_minutes": 60},
  "profile": {"instance_count": 99, "solution_limit": 2, "tolerate_inconclusive": true,
              "execution_timeout": 180, "reference_timeout": 180,
              "compilation_timeout": 120, "memory_mb": 2048, "cpus": 1}
}
```

`instance_count: 99` is the setting that matters: a count above the supply is a
budget rather than an error, so one number checks every distinct instance of
every problem, and a model that fitted the example dies on the second one. The
cost lands in the right place, since a wrong model fails early and stops.
`tolerate_inconclusive` skips an instance that only times out instead of ending
the pair, and `solution_limit: 2` gives the search a second chance to surface a
wrong solution. Drop `solution_limit` to 1 when the integration declares
`enumeration: false`, or the result is `unsupported_capability`.

The profile is frozen for the run. Use one run per integration when capabilities
differ, and never weaken a profile mid-run to turn a failure into a pass.

## The loop, one pair at a time

1. **Check readiness.** `generation.manage attempt` requires a current
   `solvers/<id>/readiness.json`, and evaluation and retention re-check it. Never
   bypass that gate: it is what stopped an earlier trial from claiming an
   untested integration was fine.
2. **Write the brief from the reference.** The reference
   (`dataset/<problem>/<problem>.cpmpy.py`) *is* the specification, and your job
   is to express the same problem in the target framework. Read it and take the
   description, the declared instance inputs, the output keys with their types
   and shapes, the objective direction if there is one, and the constraints
   themselves. Translating its semantics is the work, not a shortcut.

   Three things that reading it does **not** license. Never execute its solve
   tail. Never carry over a constraint the reference has commented out — several
   references keep symmetry breaking between
   `<SYMMETRY_BREAKING_CONSTRAINT_START>` and `..._END>` markers, which is not
   part of the contract. And never embed an answer: a solution computed by
   running the reference, or any branch on which instance you were given, is the
   one failure this whole system exists to catch.

   Take the output **keys** from the reference's `solution = {...}` dictionary,
   not from its variable names: they differ. Number partitioning builds `x` and
   `y` and declares them as `A` and `B`, and getting that wrong is an
   `invalid_output`, not a modelling error you can reason your way out of. A
   declared output may also be an expression rather than a variable — Golomb
   rulers declares `length` as `marks[-1]` — which is fine to mirror.

   A missing or self-contradictory specification is a reference blocker — record
   it and move to another pair rather than guessing.
3. **Open the attempt**, which freezes the modelling skill you are about to use:

   ```sh
   python -m generation.manage attempt --run <run-id> --problem PROBLEM --solver SOLVER --skill solvers/SOLVER/skills/NAME
   ```

   Use the path it returns. Save the brief next to the attempt.
4. **Read the frozen modelling skill** for that integration and write the model
   into the attempt directory. It must be instance-agnostic: it takes the
   instance data and builds the model from it. Fixed mathematical constants are
   fine. Embedding a known answer, or branching on which instance it was given,
   is not — that is the one failure this whole system exists to catch.
5. **Evaluate through the helper**, which preserves the exact evaluated bytes:

   ```sh
   python -m generation.manage evaluate --attempt ATTEMPT_PATH --model MODEL_PATH
   ```

6. **If it was rejected**, read `reason` and `detail` and route the failure with
   the table in [the run protocol](references/run-protocol.md). Repair the model
   and open a *new* attempt; never overwrite a previous one. Do not resubmit an
   unchanged candidate. After the attempt cap, mark the pair exhausted, keep
   every attempt, and go to the next pair.
7. **If it was accepted**, apply the correctness rule below, then retain:

   ```sh
   python -m generation.manage retain --attempt ATTEMPT_PATH
   ```

8. **Commit that one model before starting the next pair**, so the history has
   one commit per accepted model and an interrupted run always resumes from a
   clean state. Then return to step 1.

## Deciding a model is correct

Do not move to the next pair until you can say why this model is right. Before
retaining, confirm all of the following from the evaluation record itself, not
from your own expectation:

- `accepted` is `true` and the reason is `accepted`.
- `unperformed_instances` is empty. Without `tolerate_inconclusive`,
  `instances_checked` equals `min(profile instance_count, instances_available)`;
  with it, read `skipped_instances` and check the reason on each skipped
  instance, because the two timeouts mean opposite things:
  - `reference_timeout` — the reference itself could not be solved. Nothing
    about your model is implicated, and no amount of repair will help.
  - `execution_timeout` — your model ran and *your* solver was too slow. That
    is a repair signal: a missing bound, a weak encoding, or a framework that
    is simply the wrong tool for this problem. Tolerating it is legitimate, but
    report it as a performance limit rather than implying the problem was
    blocked, and say which instances the model is actually evidenced on.
- `solutions_checked` is at least 1 and within the requested limit.
- The retained `model_hash` matches the bytes you wrote.

Then do the check the evaluator cannot do for you. **141 of the 164 problems
have only the embedded example**, so for most of the corpus there is no second
instance to expose a model that simply hardcoded the first one. `next_work`
reports `instances` per pair and offers many-instance problems first for exactly
this reason; on a single-instance problem an accepted result tells you almost
nothing about generality.

So before retaining, read your model and confirm every quantity that belongs to
the instance is taken *from* the instance argument — not typed in. A model whose
`build` never reads its argument has hardcoded the example, whatever the
evaluator said. This has already happened once in this repository: the first
accepted model, for `abbots_puzzle`, hardcodes all its constants and passed,
because that problem has exactly one instance.

The evaluator also never proves a model is *right*: it only ever finds a
counterexample or fails to. A model that passes every instance may still be
narrower than the problem. That judgement is yours.

Reduced coverage is acceptable **only** when the cause is a recorded reference or
infrastructure limit — for example the reference timing out on a later instance —
never a model failure. When that happens, record the limit, retain with the
coverage actually achieved, and state the reduction in your report. If the
failure is the model's, the model is wrong; fix it.

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

## When a failure teaches something general

Some failures teach you about the framework: an API needs integer coefficients,
a constraint has a different name than you assumed. That belongs in the
integration's modelling skill so the next model benefits. Problem-specific
insight belongs in that pair's attempt history and nowhere else — otherwise the
skill decays into a pile of unrelated patches.

A skill change needs evidence and a regression, never just a hunch: follow the
propose/check/apply procedure in [operations](references/operations.md). One
failure does not prove what caused it. Record a proposal you decided against,
with your reasoning.

## Rules that do not bend

- Never edit a reference, the dataset, the evaluator, or the runner to make a
  model pass. If you believe a reference is wrong, record it as a blocker and
  leave it alone.
- Never weaken the profile, skip an instance, or reinterpret a failure to
  manufacture a pass.
- Never call something accepted without an evaluator record that says so. A
  clean build, an empty stderr, and your own reading of the model are not
  acceptance.
- Never overwrite a previous attempt, a retained model, or a legacy directory.
- Never work on a branch you did not create for this run, and never push or
  install skills globally.
- Never touch an integration you are not setting up, and never edit
  `runner/runtime.py` or `runner/requirements.txt` to suit a new one. Both are
  shared with every existing image, so a change there invalidates integrations
  that are already certified. A new integration gets its own `run.py` and its own
  Dockerfile dependencies.
- An unavailable Docker engine, a missing licence, or an exhausted budget is a
  concrete blocker to report — not a reason to claim the work is finished.

## Finish

Report: each accepted model with its retained path and the coverage actually
achieved; pairs left exhausted or blocked with the reason; integrations created
or repaired; skill changes applied or left pending; and the budget you used.
Say plainly what you did not verify. If the run was interrupted, checkpoint it
as interrupted — never as complete.
