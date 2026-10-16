# Integration files

What `solvers/<id>/` must contain beyond the standalone skill, and the rules the
repository enforces on it. The runner realises the submission contract `solvers/CONTRACT.md`,
and `solvers/<id>/CONTRACT.md` documents how. Repository `evaluation/README.md` (runner protocol) and
`tests/test_solvers.py` are the current contract; read them when this summary and the
code disagree.

Check your work against this page with

```bash
python <this-skill>/scripts/check_integration.py ID --static   # while building; no Docker needed
python <this-skill>/scripts/check_integration.py ID            # at the end: also verifies readiness.json
```

It prints PASS/WARN/FAIL per rule and exits 1 on any failure. It checks files and
metadata, not behaviour: that is what `readiness_test.py` is for.

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
- **`readiness_level: 2`** for every new integration: it adds the bug-class readiness checks
  below. An existing integration without the key is at level 1 until it is upgraded.
- **`instance_binding`** says which instances this runner can bind, so `next_work`
  withholds the pairs it never could. Omit it (`"any"`) when the submission reads the
  instance itself. `"rectangular_uniform"`: the data interface takes only rectangular,
  single-type arrays, and pairs with ragged or mixed-type fields are withheld.
  `"reshaped"`: the runner reshapes fields itself (padding, splitting) and decides what it
  cannot bind through a `refusal(name, value)` function in `run.py` that `generation.brief`
  imports on the host, so it must not import the solver or write to stdout; see
  `essence_prime_minion` and `idp_z3`. Refusal covers reshaping only, never strings: a
  string field is refused at run time, and only when the model declares it.
- **`name`** is what the website shows; the `id` never is. A library that drives one
  solver is named after that solver with the host language in brackets: `CPLEX (Python)`,
  `Choco (Python)`, `OR-Tools CP-SAT (C++)`; its package name (`docplex`, `pychoco`) goes
  in `framework`. A modelling layer over several solvers is named after the layer:
  `CPMpy (Python)`, `PuLP (Python)`, `JuMP (Julia)`. A system with its own language stands
  alone: `MiniZinc`, `Picat`, `clingo`, `SWI-Prolog`. Neither the paradigm nor the backend
  goes in the name; the backend goes in `solver`, and the website prints it beside the
  name (`MiniZinc · Gecode`). Brackets hold only the host language, never a solver or
  system. When a modelling language and the system that runs it have different names, the
  language is the name and the system goes in `solver`. Every `solver` value needs a
  display label in `BACKEND_NAMES` in `generate_site.py`, unless the name already contains
  it. Names must be distinct; `tests/test_solvers.py` and `tests/test_site.py` enforce
  these rules, and nothing can enforce a name being clear. Renaming
  is cheap: the catalogue reads `name` on every build and it is not part of the readiness
  record.
- **`language`** is what a submission is written in. It picks the label and syntax
  highlighting on the website. For a new value, add a row to `LANGUAGES` in
  `generate_site.py`; if highlight.js has no grammar for it, pair the right label with
  `plaintext`. A new `extension` also needs an `EXTENSION_LANGUAGE` entry there.
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
choice becomes the contract for every model.

When the framework binds the data (a typed modelling language), these rules kept problems
usable that would otherwise be lost:

- **Bind only the fields the model declares, and ignore the rest.** Instances carry
  metadata such as `name` and `note` (strings), and some carry data a given model does
  not need. Binding every key makes such instances fail whatever the model says.
- **Offer derived size parameters.** Languages that need finite index sets cannot declare
  a matrix whose size differs between instances. Let the model declare optional sizes per
  field (e.g. `F_dim1`, `F_dim2` for `F`) and bind them from the data; pad ragged lists and
  offer their row lengths (`F_len`); split a row of mixed types into one field per column.
- **Escape reserved words.** When an output or field name is a keyword of the language
  (`matrix`, `E`, ...), let the model use `name_` and map it back on both input and output.
- **The runner decides what is bindable.** The brief's generic `unbindable_fields` is not
  per integration and was wrong for several runners; use `instance_binding: "reshaped"`
  with the runner's own `refusal()` (above), so a pair is withheld only when this runner
  can never bind it.

Conversion always happens inside the container. **Only one submission file is staged**, so shared conversion code goes in the
image or `run.py`; anything needing extra staging is unsupported: report it.

## `run.py`

- Reads `/input/model.<ext>` and `/input/request.json`; writes JSONL `solution` records
  with `values`, then exactly one `status`. Logs go to stderr. Reuse `runner/runtime.py`
  helpers as the existing runners do.
- Never invent solutions, alter the submission, or emit more solutions than requested.
- Optimisation: prove the optimum before emitting; when enumerating, fix the objective to
  it. A timeout before proving optimality must not report success; what to emit then is
  set by the protocol in `evaluation/README.md` (`timeout`, and optimisation runners emit
  only final optimal outputs), so follow it rather than choosing per integration. Decide
  whether an objective exists before solving starts, so every kill, crash or deadline path
  knows it: the evaluator checks solutions before the status, so an unproven incumbent
  emitted before a `timeout` is rejected as suboptimal, not treated as inconclusive. Fewer
  solutions than requested only with `complete` (exhausted).
- **Count distinct declared outputs, not solver solutions.** Solvers enumerate over every
  variable, so a model with a free auxiliary variable returns the same outputs several
  times. Deduplicate on the declared outputs and re-solve with a nogood on each assignment
  already found until the count is reached or the search is exhausted.
- **Parenthesise the objective when you re-post it** (e.g. as `(objective) = optimum` to
  enumerate at the optimum). In languages where a quantifier or sum extends as far right
  as possible, the appended text is otherwise swallowed by the objective. In an API with a
  strict-bound call, check from the docs and a test whether "better than the bound" is
  already strict: an off-by-one there skips the true optimum.
- **Check emitted solutions with the solver's own checker when it has one.** A solver can
  return assignments that violate the model: ACE accepted wrong tuples for a product of
  four or more variables. Reject such solutions and continue the search instead of passing
  them on.
- **A failure is never a timeout.** A solver crash, an out-of-memory, a reserved-identifier
  error or a compile error must come back as `error` (or `compilation_error`) with the
  tool's own message in the detail. Solvers often print it somewhere unusual (a log file,
  stdout, a verbose flag only); find it and forward it. When the message is hidden,
  modelling agents cannot fix their model and start running it outside the container to
  see what went wrong. The protocol owns the real stdout: send the solver's own stdout to
  stderr.
- Return explicit `unsupported`, `error` and `compilation_error` statuses.

## `Dockerfile`

Pin the base image by digest and every dependency by version. The image must work
unprivileged, read-only, without network and with bounded scratch space; compilation
happens inside the container within its own budget. Check `.dockerignore` before relying
on a build file; never widen the context to datasets, references, credentials or models.
Verify the final `ENTRYPOINT` invokes the intended runner.

## `CONTRACT.md`

The integration contract, for modellers: how this runner realises `solvers/CONTRACT.md`.
Use exactly the headings of that file's *Mapping checklist* (`## Submission file`,
`## Entrypoint`, `## Instance`, `## Outputs`, `## Objective`, `## Solving`,
`## Compilation`, `## Environment`, `## Traps`, `## Example`) and follow an existing one
such as `solvers/cpmpy_python/CONTRACT.md`. State what the code does, not what you meant
it to do: signatures, the instance representation, the output container, the objective
form, the settings the runner forces. Every fact about the container (binary paths,
environment variables, network, preinstalled packages) goes under `## Environment`, never
into the standalone skill. Put the pilot fixture in `## Example`. Leave out what `solvers/CONTRACT.md` already says and
what the standalone skill teaches about the solver's API. A model attempt refuses an
integration without this file, and records its hash.

## `readiness_test.py`

Adapt an existing one (`solvers/cpmpy_python/readiness_test.py` is the cleanest). It
drives the real evaluator against the built image, prints a JSON object of check name to
Boolean, and exits nonzero on any failure. Required checks: `satisfaction`,
`changed_instances`, `malformed_output`, `empty_output`, `timeout_cleanup`, `isolation`,
`missing_image`; `minimization` and `maximization` (or `unsupported_optimization`);
`enumeration` (or `unsupported_enumeration`); `compilation_error` when compiled. The
exact list is in repository `generation/AGENTS.md`. Write each check to be able to fail.

Beyond the required names, add a check that a solver crash is reported as `error` with the
solver's own message in the detail. Without it, modelling agents cannot see why a model
failed.

### Bug-class checks (`readiness_level: 2`)

Tiny `x + y` models prove their optimum instantly and output flat integers, so they never
reach the runner bugs that real models hit. Each of these checks covers one class that a
modelling campaign exposed in some integration; `solvers/cpmpy_python/readiness_test.py`
implements all of them, with a trusted reference each. Write the submission in this
integration's own form, and make each check able to fail.

| Check | Bug class | The submission, and what must happen |
|---|---|---|
| `optimization_timeout` | an unproven optimum emitted when time runs out | an easy reference; the submission adds an unrelated hard part to its objective (a Golomb ruler) so the solver finds a solution fast but cannot prove it within a 3 s budget: `execution_timeout` with **zero solutions received** |
| `minimization_step_one` | an off-by-one bound in a runner that bounds the objective itself | a minimisation whose first solution is exactly optimum + 1 (steer the search there if the runner does branch and bound): accepted |
| `optimum_enumeration` | a re-posted objective parsed or pinned wrongly | a compound objective (a sum) with ten optima, `solution_limit=3`: accepted with 3 solutions checked |
| `output_shapes` | outputs the runner cannot carry | a three-level integer array, a Boolean matrix and a value beyond 32 bits: accepted, or `unsupported` with the limit documented under `## Outputs` |
| `instance_shapes` | instance binding | ragged rows, rows of mixed types, an unused string field and `name`/`note`, on two instances of different shapes: accepted (for `rectangular_uniform`, the refusal the contract documents) |
| `error_detail` | errors hidden as timeouts or bare exit codes | a submission that makes the solver or its library raise: `execution_error` with that tool's own message in the detail |
| `stray_stdout` | solver or model output corrupting the protocol | a submission that prints: accepted |
| `auxiliary_free_distinct` | duplicate outputs from free auxiliaries | a free auxiliary variable outside the outputs, `solution_limit=3`: accepted with 3 distinct solutions |
| `large_model` | stack and recursion limits | a sum over 3000 Booleans, used as an output: accepted within 120 s |

The checks that need optimisation or enumeration are required only when the metadata
declares those capabilities.

## Once certified

`tests/test_solvers.py` requires every integration with a `readiness.json` to be a pilot:
add it to `PILOTS` with a fixture model under `tests/fixtures/`, and, unless it cannot
optimise, to `MAXIMIZATION_SWAPS` with the minimise/maximise spelling that fixture uses.
`README.md` must name the integration by its `name`.

The readiness record binds the image identity and the hashes of `run.py`, `Dockerfile`,
the check script and every `metadata.yaml` field except `name` and `paradigms`, so
changing any of those means running the check again. The record is write-once: to
re-certify after a fix, rebuild the image, delete `readiness.json`, then run `check` and
`verify` again. While models are being evaluated on the `:v1` image, build and test a
runner fix on a separately tagged image, and rebuild `:v1` only once no evaluation is
running on it.
