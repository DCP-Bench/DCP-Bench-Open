# Integration files

What `solvers/<id>/` must contain beyond the standalone skill, and the rules the
repository enforces on it. Repository `evaluation/README.md` (runner protocol) and
`tests/test_solvers.py` are the current contract; read them when this summary and the
code disagree.

## `metadata.yaml`

Read an existing `solvers/*/metadata.yaml` and **match its key set**: do not invent or
drop keys, because readiness and evaluation both read this file. The loader parses
**JSON syntax despite the `.yaml` extension**.

```json
{
  "id": "framework_language",
  "name": "CPMpy (Python)",
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

- **`id`**: lowercase letters, digits and underscores; unique and stable. Skill names use
  hyphens instead. `id`, `image`, `extension` and `enumeration` are what the evaluator
  requires.
- **`optimization: false`** only for an integration that genuinely cannot optimise, and
  **`compilation: true`** only for one that compiles. Both change which readiness checks
  are required. Use literal Booleans and never advertise a capability that was not tested.
- **`name`** is what the website shows; the `id` never is. A library that drives one
  solver is named after that solver with the host language in brackets: `CPLEX (Python)`,
  `Choco (Python)`, `OR-Tools CP-SAT (C++)`; its package name (`docplex`, `pychoco`) goes
  in `framework`. A modelling layer over several solvers is named after the layer:
  `CPMpy (Python)`, `PuLP (Python)`, `JuMP (Julia)`. A system with its own language stands
  alone: `MiniZinc`, `Picat`, `clingo`, `SWI-Prolog`. Neither the paradigm nor the backend
  goes in the name; the backend goes in `solver`, and the website prints it beside the
  name (`MiniZinc · Gecode`). Names must be distinct (`tests/test_solvers.py`). Renaming
  is cheap: the catalogue reads `name` on every build and it is not part of the readiness
  record.
- **`language`** is what a submission is written in. It picks the label and syntax
  highlighting on the website. For a new value, add a row to `LANGUAGES` in
  `generate_site.py`; if highlight.js has no grammar for it, pair the right label with
  `plaintext`.
- **`paradigms`** is required. Use IDs from `solvers/paradigms.json`, tagging the paradigm
  a **submission is written in**, not the backend's technology: CP-SAT is `["cp"]`.
  Declare several tags when a submission really belongs to more than one (`swipl_clpfd`
  is `["cp", "clp"]`). If nothing fits, add an entry to `solvers/paradigms.json` in the
  same commit; `tests/test_solvers.py` fails on an unknown tag.

## Who converts the instance

The decision with the most consequences. Pick the pattern closest to how the standalone
skill already models.

| Pattern | Who converts | Used by |
| --- | --- | --- |
| the model reads the dict | the submission, via `instance["n"]` | `cpmpy_python`, `ortools_cp_sat_python`, `z3_python` |
| the framework binds it | `run.py`, feeding each JSON key to the framework's data API | `minizinc_gecode` |
| a harness parses it | code baked into the image, handing the parsed object to a fixed entrypoint | `ortools_cp_sat_cpp` |

A framework whose input is generated source (facts for an ASP grounder, a bespoke data
file) fits none cleanly: either the submission emits that text or `run.py` does, and that
choice becomes the contract for every model. Conversion always happens inside the
container. **Only one submission file is staged**, so shared conversion code goes in the
image or `run.py`; anything needing extra staging is unsupported: report it.

## `run.py`

- Reads `/input/model.<ext>` and `/input/request.json`; writes JSONL `solution` records
  with `values`, then exactly one `status`. Logs go to stderr. Reuse `runner/runtime.py`
  helpers as the existing runners do.
- Never invent solutions, alter the submission, or emit more solutions than requested.
- Optimisation: prove the optimum before emitting; when enumerating, fix the objective to
  it; count distinct declared outputs. A timeout before proving optimality is `timeout`,
  never success. Fewer solutions than requested only with `complete` (exhausted).
- Return explicit `unsupported`, `error` and `compilation_error` statuses.

## `Dockerfile`

Pin the base image by digest and every dependency by version. The image must work
unprivileged, read-only, without network and with bounded scratch space; compilation
happens inside the container within its own budget. Check `.dockerignore` before relying
on a build file; never widen the context to datasets, references, credentials or models.
Verify the final `ENTRYPOINT` invokes the intended runner.

## `readiness_test.py`

Adapt an existing one (`solvers/cpmpy_python/readiness_test.py` is the cleanest). It
drives the real evaluator against the built image, prints a JSON object of check name to
Boolean, and exits nonzero on any failure. Required checks: `satisfaction`,
`changed_instances`, `malformed_output`, `empty_output`, `timeout_cleanup`, `isolation`,
`missing_image`; `minimization` and `maximization` (or `unsupported_optimization`);
`enumeration` (or `unsupported_enumeration`); `compilation_error` when compiled. The
exact list is in repository `generation/AGENTS.md`. Write each check to be able to fail.

The readiness record binds the image identity and the hashes of `run.py`, `Dockerfile`,
the check script and every `metadata.yaml` field except `name` and `paradigms`, so
changing any of those means running the check again.
