---
name: solver-setup
description: Add or repair a DCP-Bench (Rosetta) solver integration. Runs the add-solver skill to generate a standalone skill for the solver, then adds the Rosetta infrastructure (metadata, Docker image, runner, readiness test) so models written with that skill can be evaluated. Use when model-generator needs an integration that is missing or broken.
compatibility: Requires the add-solver skill, Docker, and a DCP-Bench Open checkout with its Python environment
metadata:
  requires-skills: add-solver
---

# Solver setup

Two layers. **add-solver** produces a standalone skill that teaches the solver itself.
This skill adds what Rosetta needs around it: `metadata.yaml`, `Dockerfile`, `run.py`,
`readiness_test.py` and a readiness record. How a Rosetta submission must look is
model-generator's job, not this one's.

Paths to `generation/`, `evaluation/`, `solvers/` and `skills/` mean repository-root
paths. Return **ready** or **blocked** to the caller.

## 0. Requires add-solver

Find `SKILL.md` of add-solver at `skills/add-solver/` in the repository, or in the agent's
skill directories (`.claude/skills/`, `~/.claude/skills/`, `.agents/skills/`). If it is
missing, stop: return **blocked** and tell the user to install it with

```bash
npx skills add DCP-Bench/DCP-Bench-Open --skill add-solver
```

Never reconstruct its steps from memory. Note its path in the setup notes: the setup
attempt freezes only this bundle.

## 1. Inputs and bookkeeping

The caller gives the target (solver, language, backend), the capabilities it needs
(satisfaction, optimisation, enumeration), the remaining budget and the error, if any.
Run on your own, follow `AGENTS.md`, start a run with
`python -m generation.manage init --run RUN`, and default to one integration, two
attempts and 30 minutes. Never start a nested run when called from model-generator.

Before writing any file, record the attempt:

```bash
python -m generation.manage setup-attempt --run RUN --solver ID --skill rosetta-skills/solver-setup
```

Reuse an existing integration when it really supports the target; never relabel another
solver to claim the target works. Do not change evaluator or reference acceptance logic or
disable isolation. A target that needs a protocol change is a blocker with a proposal.
Details: [operations](references/operations.md).

## 2. Generate the standalone skill

Follow add-solver. Its step 0 questions are answered here:

| add-solver asks | Answer |
|---|---|
| Solver and language | The caller's target |
| Where to write the skill | `solvers/<id>/skills/<framework>-<language>/` |
| Workspace | `generation/runs/RUN/setup/<id>/<attempt>/add-solver-workspace/` |
| How thorough | Thorough, unless the budget forbids it; then quick, and say so |

Two Rosetta rules on top:

- **Nothing is installed on the host.** Write the `Dockerfile` first (step 3), build it,
  and run add-solver's probes and toy tests inside the image, e.g.
  `run_toy_tests.py --cmd 'docker run --rm --network none -v "$PWD":/w -w /w --entrypoint python IMAGE <workspace>/round-N/models/{problem}.py {instance}'`.
- **The skill stays standalone.** No DCP-Bench, runner or submission instructions in it;
  it must work outside this repository. Also validate it with
  `python -m generation.skills validate --project <skill-folder>`.

## 3. Add the Rosetta infrastructure

Copy the closest existing integration under `solvers/` (same language, or same way of
receiving the instance) and adapt `metadata.yaml`, `Dockerfile`, `run.py` and
`readiness_test.py`. The rules for each file, and the choice of who converts the JSON
instance, are in [integration files](references/integration.md). Check them as you go:

```bash
python <this-skill>/scripts/check_integration.py ID --static
```

Build with `python -m evaluation.build <id>`, bounded by the remaining budget. Evaluation
never builds or installs implicitly.

## 4. Readiness

```bash
python -m generation.readiness check --solver ID --output solvers/ID/readiness.json
```

This runs `solvers/<id>/readiness_test.py` against the built image and records the result
only when every required check passes. Tests skipped because Docker or the image is
missing do not count. Then register it as a pilot (see *Once certified* in
[integration files](references/integration.md)) and run `scripts/check_integration.py ID`
without `--static`: it must exit 0 before you return **ready**. After changing shared runner code, rerun the affected existing
integrations too.

## 5. Return

Write the evidence under `generation/runs/RUN/setup/<id>/`: changed files, sources,
versions, commands and their output, image identity, capabilities and limitations, and
add-solver's report with its toy-test table. Record `setup_finished` or `setup_blocked`
with `generation.manage event`.

Return **ready** only after readiness passed. Otherwise return **blocked** with the exact
failure, the attempts spent and what is left. Stop when the budget is spent; never
recurse.

Releasing the standalone skill to the public `skills/` folder is the user's call, not part
of setup. Name the command as the next step:
`python -m generation.release publish <id> -m "First release"`.
