---
name: solver-setup
description: Create or repair a DCP-Bench solver integration from official documentation, including pinned container environment, runner, capability metadata, portable modelling skill, and real evaluation tests. Use when model-generator selects a missing or broken language/framework/backend integration.
---

# Solver setup

Return a tested integration or an evidence-backed blocker to the caller. Work
inside the caller's repository, branch, owned paths, run ID, and remaining budget.
When invoked alone, locate DCP-Bench Open, follow AGENTS.md, initialize a run with
`python -m generation.manage init --run RUN`, and default to one integration,
two setup attempts and 30 minutes. Do not initialize a nested run when called
from model-generator.

Read [operations and learning](references/operations.md) first. All paths to
`generation/`, `evaluation/`, and `solvers/` mean repository-root paths, so this
bundle can be installed elsewhere. The generation helper modules are explicit
repository prerequisites. Never install candidate libraries on the host.

## Inputs and scope

Receive the exact language/framework/backend target, required satisfaction and
optimization/enumeration capabilities, current error if any, allowed setup
attempts, remaining wall time, and owned integration/test/skill paths. Clarify
only material ambiguity (e.g. a commercial license or unavailable requested
backend); research ordinary API/build choices through official documentation.

Read repository `evaluation/README.md`, `evaluation/execution.py`,
`evaluation/build.py`, relevant `runner/` code, `.dockerignore`, and
`tests/test_solvers.py`. They define the actual current contract. Reuse an existing
integration when it really supports the target; never relabel a different solver
to claim the requested framework works.

Do not change evaluator/reference acceptance logic, disable isolation, install
candidate dependencies on the host, or start another generation coordinator.
An extension needing evaluator protocol changes returns a concrete blocker and
proposal for a separate task. Keep setup changes isolated from passing integrations.

## Produce the integration

1. Record authoritative API/build sources and exact dependency versions. Resolve
   licensing/platform requirements. Use a unique stable integration ID for the
   language/framework/backend combination, preserving existing IDs.
2. Create `solvers/<id>/metadata.yaml`, `run.py`, and `Dockerfile`. Read an
   existing `solvers/*/metadata.yaml` and **match its key set** — do not invent
   or drop keys, because readiness and evaluation both read this file:

   ```json
   {
     "id": "framework_language",
     "name": "CPMpy",
     "language": "python",
     "framework": "cpmpy",
     "solver": "ortools",
     "paradigms": ["cp"],
     "image": "dcp-eval/framework_language:v1",
     "extension": ".py",
     "enumeration": true,
     "protocol_version": 1
   }
   ```

   **`name` is what the community reads on the website, and the `id` is never
   shown.** Name the integration after what a model author writes, and add a
   qualifier only when an existing integration would otherwise be
   indistinguishable from it. The backend solver belongs in `solver`, never in
   the name: a MiniZinc model is the same text whether Gecode or Chuffed runs
   it, so the integration is `MiniZinc`. A qualifier earns its place when it
   changes what gets written — `OR-Tools CP-SAT (Python)` against
   `OR-Tools CP-SAT (C++)`, or `SWI-Prolog CLP(FD)`, whose models open with
   `:- use_module(library(clpfd))` and constrain with `#=`. Prefer a package
   name that already carries the language, as `CPMpy` and `PyChoco` do, over
   spelling it out. Names must be distinct; `tests/test_solvers.py` enforces
   that much, and nothing can enforce a name being clear.

   Renaming is cheap: the catalogue resolves `name` from this file on every
   build, so no retained model has to be touched. Do not add a display name to
   `record.json`.

   `id`, `image`, `extension` and `enumeration` are what the evaluator requires.
   Add `"optimization": false` only for an integration that genuinely cannot
   optimize, and `"compilation": true` only for one that compiles; both change
   which readiness tests are required, so declaring them wrongly either hides a
   gap or demands a test that makes no sense. Use literal Booleans, and never
   advertise a capability that was not tested.

   **`language` names what a submission is written in, and the website reads
   it.** It picks the label and the syntax highlighting above every model of
   this integration, so `cpp` gets a block headed `C++` and `prolog` one headed
   `Prolog`. Add a row to `LANGUAGES` in `generate_site.py` for a value that is
   not there yet: it maps the language to a highlight.js grammar and a label.
   highlight.js ships 36 grammars in the bundle the site loads; for a language
   it has none for, pair the correct label with `plaintext` rather than a
   grammar that would colour the model as something it is not.

   **`paradigms` is required, and it is not decorative.** The catalogue website
   groups every verified model by it, so an integration that omits the key or
   invents a tag either vanishes from the breakdown or silently splits a column
   in two. Use one or more IDs from `solvers/paradigms.json`, which is the whole
   vocabulary and describes what a model in each paradigm looks like. Tag the
   paradigm a **submission is written in**, not the technology the backend
   solves with: a CP-SAT integration is `["cp"]` even though its core is a SAT
   solver, because a CP model is what the modeller writes. Declare several tags
   when a submission genuinely belongs to more than one — `swipl_clpfd` is
   `["cp", "clp"]`, because a CLP(FD) model is a constraint model and someone
   looking for a CP encoding should be shown it. If nothing fits, add the
   entry to `solvers/paradigms.json` in the same commit, saying in prose what a
   model in that paradigm looks like — `tests/test_solvers.py` fails on a tag
   that is not in the file.

   The loader parses **JSON syntax despite the `.yaml` extension**; emit a JSON
   object, not general YAML. Integration IDs allow lowercase letters, digits and
   underscores; skill names instead use hyphens. Keep those separate.
3. Implement the current runner protocol: `/input/model.<ext>` and
   `/input/request.json`; JSONL solution records with `values`, followed by exactly
   one final status. Keep logs on stderr. Return explicit unsupported/error/
   timeout/compilation statuses. The runner must not invent solutions, silently
   alter the submission, or output more solutions than requested.
4. **Decide who turns the JSON instance into the framework's input, and say so
   in the modelling skill.** This is the design decision with the most
   consequences, and the three existing integrations answer it three ways:

   | Pattern | Who converts | Used by |
   | --- | --- | --- |
   | the model reads the dict | the submission, via `instance["n"]` | `cpmpy_python`, `ortools_cp_sat_python`, `z3_python` |
   | the framework binds it | `run.py`, feeding each JSON key to the framework's own data API | `minizinc_gecode` |
   | a harness parses it | code baked into the image, handing the parsed object to a fixed entrypoint | `ortools_cp_sat_cpp` |

   The first two suit a framework whose model is an API you call or a file with
   declared parameters. A framework whose input is *generated source* — facts for
   an ASP grounder, a bespoke data file — fits none of them cleanly: either the
   submission emits that text itself, or `run.py` does, and whichever you choose
   becomes the contract every model for this integration must follow. Choose
   deliberately rather than by accident, and write the choice into the skill with
   a worked example.

   Conversion always happens inside the candidate container. **Only one
   submission file is staged**, so a submission cannot ship a helper module: put
   shared conversion in the image or in `run.py`. Anything needing extra staging
   is unsupported today — report it rather than working around it.
5. Implement minimization/maximization semantics honestly: establish optimum
   before emitting optimal assignments, fix it when enumerating, and count
   distinct declared outputs. A timeout before proving optimum must not report
   success. Satisfaction enumeration may finish below the requested count only
   on exhaustion. Mark unsupported enumeration explicitly.
6. Pin build/runtime dependencies and supply an image compatible with the
   evaluator's unprivileged, read-only, networkless execution and bounded scratch
   space. Compile inside the candidate container within its separate budget.
   Read the Docker context whitelist before relying on a build file; avoid
   expanding context to include datasets, reference code, credentials, or models.
7. Write the solver's modelling skill using the **Skill packaging** section below.
   Include the tested entrypoint/outputs contract, API patterns, objective/status
   semantics, supported types, exact environment versions, known limits, and
   runnable tiny examples. Separate long documentation into bundled references.
8. Build explicitly with the repository Python environment:
   `python -m evaluation.build <id>`. Bound the process by the remaining setup
   budget. Evaluation itself must never build or install implicitly. Record the
   actual image ID and test evidence, not just a mutable tag.

## Readiness gate

Create small independent tests following `tests/test_solvers.py`. Exercise the
actual image through the evaluator/runner, with explicit expected outcomes:

- Valid satisfaction, minimization, and maximization where supported; change
  instance data and verify the submission responds to it.
- Multiple distinct solutions and exhausted enumeration where advertised.
- Invalid/malformed/empty output rejection and accurate unsupported statuses.
- Compilation failure for compiled targets; execution timeout and cleanup.
- Current isolation guarantees and missing-image diagnostics.

Use tiny trusted synthetic references for integration fixtures if needed, never
replace a corpus reference to make a generated candidate pass. Reuse existing
shared tests where applicable and add target-specific invocations. Tests skipped
because Docker or an image is absent do not meet this gate. After shared runner
changes, rerun affected existing integrations as well.

Write setup evidence under the run's `setup/<solver_id>/`: files changed, sources,
versions, actual commands/results, image identity, capabilities and limitations.

Every integration ships its own check script at `solvers/<id>/readiness_test.py`.
It is a required artifact, like the runner and the Dockerfile. It must drive the
repository evaluator against the built image for every required check, print a
JSON object mapping check name to Boolean on stdout, and exit nonzero if any of
them failed. Write it against the real evaluator — an assertion about the
integration's behaviour, never a restatement of what you hope is true.

```sh
python -m generation.readiness check --solver ID --output solvers/ID/readiness.json
```

This runs your script, keeps its stdout and stderr as the evidence, and records
the result only when the script exits zero with every required check true. The
record binds the image identity and the hashes of `metadata.yaml`, `run.py`,
`Dockerfile` and the check script, so editing any of them invalidates it and the
checks must run again.

`solvers/cpmpy_python/readiness_test.py`
is a working example. See repository `generation/AGENTS.md` for the exact list of
required check names. One green smoke test does not cover all failure cases. Verify the image's final ENTRYPOINT
invokes the intended callable; do not assume a shared runtime module runs itself.
Return **ready** only after real tests pass; otherwise return **blocked**, exact
failure, attempts spent, and remaining work. The coordinator then resumes the
original pair or continues elsewhere. Stop after its setup budget; no recursion.

## Skill packaging

Apply [the skill standard](references/skill-standard.md). For a new integration, a self-contained standard bundle can live at
`solvers/<id>/skills/<hyphenated-skill-name>/SKILL.md`. Its sibling resources live
inside that same bundle. Keep `solvers/<id>/SKILL.md` as a short repository-facing
pointer to the canonical bundle so existing discovery still works; the pointer
is not another installable skill. Existing direct instructions can remain until
explicitly packaged; avoid wholesale migration during an unrelated setup.

Do not keep duplicate editable instruction copies. Installing a skill means
copying/linking the complete canonical bundle to the authorized client's skill
directory, preserving its folder name and resources, then verifying discovery
using that client's documented mechanism. Repository creation alone does not
mean an agent client has installed or activated it. Global installation requires
user scope; the generator can read the repository bundle directly without it.
