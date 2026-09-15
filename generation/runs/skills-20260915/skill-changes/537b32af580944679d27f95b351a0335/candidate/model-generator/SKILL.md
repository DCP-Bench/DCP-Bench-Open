---
name: model-generator
description: Populate DCP-Bench Open with constraint models that the repository evaluator has accepted. Pick an uncovered problem and solver integration, write an instance-agnostic model, verify it against the reference, keep it, and move to the next one. Use for model generation campaigns, including building a solver integration that does not exist yet.
---

# Model generator

Add models to this repository that a real evaluator has accepted: choose a
problem and a solver integration, write a model, prove it holds up, keep it,
move on.

You need this repository, its Python environment
(`.venv/Scripts/python.exe` on Windows, `.venv/bin/python` on Unix), and a
running Docker Linux engine. Run every command from the repository root; all
paths here are relative to it. An unavailable engine is a blocker to report, not
something to work around: candidate code never runs on the host.

**You are the only agent.** You are the coordinator and the modeller; "invoke a
skill" only ever means "read that file and follow it". There are three kinds of
skill and only three: this one, the campaign loop; `skills/solver-setup`, read
only when the integration you need does not exist; and
`solvers/<id>/skills/<name>`, one per integration, read every time you write a
model for it. The third kind is the only one this workflow edits; the other two
change through the procedure in [operations](references/operations.md).

## The loop

```sh
git switch -c models/<run-id>                       # never commit to main, never push
python -m generation.manage init --run <run-id> --config config.json
python -m generation.next_work                      # what is uncovered, and what is not usable
python -m generation.brief PROBLEM                  # the contract: outputs, objective, fields
python -m generation.manage attempt --run <run-id> --problem P --solver S --skill solvers/S/skills/N
#   write the model into the attempt directory, following that integration's skill
python -m generation.manage evaluate --attempt ATTEMPT --model ATTEMPT/model.EXT
python -m generation.manage retain  --attempt ATTEMPT        # only when it was accepted
#   commit each batch of accepted models, then take the next pair
```

1. **Branch first.** The run gets a branch of its own, off whatever branch you
   are on, so its commits can be reviewed, kept or dropped as one unit. Being on
   a branch already does not satisfy this. Use the same `<run-id>` for the
   branch and the run. If the checkout has uncommitted work, stop and ask.
2. **Agree the budget** before generating. Defaults, unless the user says
   otherwise: 10 model attempts per pair, one new integration per run, two setup
   attempts per integration, 60 minutes. Stop starting new work when it is gone,
   then checkpoint what exists.
3. **Set a profile that makes a pass mean something** (below), and freeze it.
4. **Pick the work** yourself unless the user named it. `next_work` lists every
   integration with whether it is usable, the uncovered pairs, and what it is
   withholding; a pair under `unbindable_pairs` is impossible for that
   integration whatever you write, and `blocked_pairs` are recorded dead ends.
   Prefer problems with several instances when you want the evaluator itself to
   catch a hardcoded model. An integration reported as not `ready` cannot be
   used at all; legacy directories under `generated_models/` are not coverage.
5. **Read the contract, then the reference.** `generation.brief PROBLEM` prints
   the declared output names with their shapes, the objective direction, and
   every instance field with its shape. The reference
   (`dataset/<problem>/<problem>.cpmpy.py`) *is* the specification, and
   translating its semantics is the work. Three things reading it does not
   license: never execute its solve tail; never carry over a constraint it keeps
   commented out between `<SYMMETRY_BREAKING_CONSTRAINT_START>` and `..._END>`;
   and never embed an answer, whether computed by running the reference or
   branched on which instance you were given. A missing or self-contradictory
   specification is a reference blocker — record it and move on.
6. **Write the model** into the attempt directory, following the frozen
   modelling skill for that integration. It must build the model *from* the
   instance argument. Fixed mathematical constants are fine; embedding a known
   answer is the one failure this whole system exists to catch.
7. **Evaluate through the helper**, which preserves the exact evaluated bytes.
   On a rejection, read `reason` and `detail` and route the failure with the
   table in [the run protocol](references/run-protocol.md). Repair the model and
   open a *new* attempt; never overwrite one, never resubmit unchanged bytes.
   After the attempt cap, mark the pair exhausted and take the next one.
8. **Before retaining**, satisfy yourself the model is right:
   [acceptance](references/acceptance.md) says what the record has to show and
   what only you can check. Then `retain`.
9. **Commit in batches**, not once per model: a coherent group of accepted
   models in one commit — a sweep of related problems, or one integration's
   share of the run — with a message naming what it carries and any reduced
   coverage among them. Commit a batch before starting a long wait, so accepted
   work is never left uncommitted across one, and again at the end of the run.
   What makes an interrupted run resumable is the ledger, not git: `retain`
   writes `retained.json` and the record under `generated_models/` as it goes,
   and `generation.manage status` reads those back whether or not anything was
   committed.

Independent pairs are independent: nothing stops you writing several models
before evaluating, or running several evaluations at once, as long as each has
its own attempt.

## The profile is the coverage claim

Create the run once, on the branch you made, with `config.json` **inside** the
repository (the helper refuses a path outside it):

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
wrong solution — drop it to 1 when the integration declares
`enumeration: false`, or the result is `unsupported_capability`.

The profile is frozen for the run. Use one run per integration when capabilities
differ, and never weaken a profile mid-run to turn a failure into a pass.

## When something is missing, or teaches you something

- **The integration does not exist, or is not usable.** Both cases are in
  [integrations](references/integrations.md): building one means following
  `skills/solver-setup` yourself and recording the setup skill *before* writing
  any integration file; certifying an existing one whose `readiness.json` is
  missing or stale is a separate, smaller job. Neither is a reason to rebuild a
  working integration.
- **A failure taught you about the framework** — an API needs integer
  coefficients, a constraint has another name, a compiler mangles a shape. That
  belongs in the integration's modelling skill so the next model benefits, via
  the propose/check/apply procedure in [operations](references/operations.md):
  evidence and a regression, never a hunch. Problem-specific insight belongs in
  that pair's attempt history and nowhere else. Record a proposal you decided
  against, with your reasoning.
- **A pair is not worth attempting again.** Add it to
  `generation/blockers.json` with its evidence, so the queue stops offering it.

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
  shared with every certified image; a new integration gets its own `run.py` and
  its own Dockerfile dependencies.
- An unavailable Docker engine, a missing licence, or an exhausted budget is a
  concrete blocker to report — not a reason to claim the work is finished.

## Finish

Report: each accepted model with its retained path and the coverage actually
achieved; pairs left exhausted or blocked with the reason; integrations created
or repaired; skill changes applied or left pending; and the budget you used.
Say plainly what you did not verify. If the run was interrupted, checkpoint it
as interrupted — never as complete.
