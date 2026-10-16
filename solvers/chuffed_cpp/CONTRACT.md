# chuffed_cpp: how this integration realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how Chuffed in
C++ expresses it. Runner: [run.py](run.py), which calls `main("cpp")` in
[runner/runtime.py](../../runner/runtime.py) (`cpp_solver`). That compiles the submission
together with the driver [cpp/driver.cpp](cpp/driver.cpp) and the header
[cpp/dcp.h](cpp/dcp.h) using [cpp/CMakeLists.txt](cpp/CMakeLists.txt), then runs the
binary, which owns `main`, solving, enumeration and printing. The solver skill
([skills/chuffed-cpp/SKILL.md](skills/chuffed-cpp/SKILL.md)) covers the Chuffed API;
[its DCP-format examples](skills/chuffed-cpp/references/examples.md#dcp-bench-format) and
[recipes1.cpp](skills/chuffed-cpp/references/recipes1.cpp) /
[recipes2.cpp](skills/chuffed-cpp/references/recipes2.cpp) are complete submissions.

## Submission file

One C++17 source file, `model.cpp`, compiled as a second translation unit next to
`driver.cpp`. It starts with `#include "dcp.h"`, which includes the Chuffed headers
(`chuffed/branching/branching.h`, `core/engine.h`, `core/options.h`,
`core/propagator.h`, `globals/globals.h`, `primitives/primitives.h`, `support/vec.h`,
`vars/bool-view.h`, `vars/int-var.h`, `vars/modelling.h`) and `<nlohmann/json.hpp>`, and
declares `using nlohmann::json;`. Include anything else from the standard library
yourself. The file defines `Build` and **no `main`**; it does not call `engine.solve`,
`parseOptions` or `output_vars` (the driver does all three, or their equivalent).

## Entrypoint

```cpp
void Build(const json& instance, json& outputs);
```

A free function in the global namespace with exactly this signature. It posts the model
on Chuffed's process-wide globals (`engine`, `so`) with the usual calls (`newIntVar`,
`createVars`, `int_linear`, `all_different`, `branch`, `optimize` ...) and fills
`outputs`. There is no `Problem` subclass to write: the driver supplies one.

`Build` runs **once per solving phase**, each time in a fresh `fork()`ed child process
(Chuffed's globals cannot be reset): once for a satisfaction problem or a solution limit
of 1, twice for an optimisation problem with a solution limit above 1. It must build the
same model each time.

## Instance

`instance` is the request's `instance` object as an `nlohmann::json`, 0-based. Read with
`instance.at("n")` (converts implicitly to `int`, `std::vector<int>`,
`std::vector<std::vector<int>>`, `std::string` ...) or `.get<T>()`:
`instance.at("w").get<std::vector<int>>()`, `instance.at("m")[i][j].get<int>()`. JSON
Booleans stay JSON Booleans: read them with `.get<bool>()`, as the fixture does. Ragged
arrays are ordinary nested arrays (`instance.at("rows")[i].size()`). Chuffed constraints
take `vec<int>` / `vec<IntVar*>` lvalues, not `std::vector`: copy the data into a `vec`
with `push`. A missing field (`instance.at` throws) or any other exception thrown from
`Build` becomes status `error` with the exception message as detail.

## Outputs

Set `outputs` to a non-empty JSON **object** keyed by exactly the declared output names.
Every leaf is the integer returned by **`dcp::out(IntVar*)`**, nested in JSON arrays to
the declared shape (a matrix is an array of row arrays):

```cpp
json cols = json::array();
for (int i = 0; i < n; ++i) cols.push_back(dcp::out(queens[i]));
outputs = {{"queens", cols}, {"total", dcp::out(total)}};
```

`dcp::out` registers the variable and returns its index; it may be called twice on one
variable (`dcp::out(nullptr)` throws). At each solution the driver replaces every index
with that variable's `getVal()`, so every reported value is an integer.

- **Only `IntVar*` can be an output.** A `BoolView` cannot go to `dcp::out`: a Boolean
  output is a 0..1 `IntVar` linked with `bool2int(boolView, intVar)`, reported as `0`/`1`.
  A 0..1 `IntVar` array used directly as decisions needs no `bool2int`.
- **An output variable must hold exactly the value the reference reports.** For a sum, a
  count or another expression create an `IntVar` constrained equal to it (`int_linear(...,
  IRT_EQ, total)`); for a constant use `getConstant(k)`.
- A leaf that is not an integer, or an index never returned by `dcp::out`, is status
  `error` ("Output leaves must be variable indices", "Invalid output variable index"); an
  empty or non-object `outputs` is `error` ("Expected output dictionary").
- Values are 32-bit `int` and Chuffed domains stay within ±500,000,000. There is no
  digits helper here: a declared output that can exceed that range (a 10-digit number)
  is reachable only if its declared shape lets it be split into digits or blocks;
  otherwise the problem is out of reach for this integration.

## Objective

Call `optimize(obj, OPT_MIN)` or `optimize(obj, OPT_MAX)` **once** in `Build`, on one
`IntVar*` (integer only), in the direction the brief gives. Chuffed has no expressions:
build `obj` as an `IntVar` (e.g. `int_linear(coeffs, vars, IRT_EQ, obj)`). If the
objective is also a declared output, export it with `dcp::out(obj)`. No `optimize` call
for a satisfaction problem. Do not bound `obj` with a value known from elsewhere.

## Solving

The driver ([driver.cpp](cpp/driver.cpp)) forks one child per phase. The child runs
`Build`, then, before solving:

- registers the variables passed to `dcp::out` with `output_vars`, so Chuffed blocks each
  solution on the declared outputs and auxiliaries are not compared;
- **appends branching** after whatever `branch(...)` calls `Build` made: one
  `VAR_INORDER` group over every integer variable in creation order, then the SAT
  solver's VSIDS over the remaining Booleans. Without a `branch` of your own the search
  therefore follows creation order over auxiliaries, which is poor: declare `branch` on
  the main decision variables;
- **overrides** `so.vsids = true`, `so.print_sol = false`, `so.nof_solutions` (see
  below) and `so.time_out` (the time left), redirects Chuffed's output stream and the
  child's stdout to stderr, and installs its own solution callback. Every other `so.*`
  field set in `Build` is kept, in every phase (restarts: `so.restart_type = LUBY;
  so.restart_scale = 1000;`, `so.toggle_vsids`, `so.sat_polarity`, `so.branch_random`).

Then `engine.solve` runs on one thread. Chuffed's end status maps to `sat` (stopped at
the solution limit, `RES_SAT`), `unknown` (time out, `RES_UNK`) or `finished` (search
complete).

- **Satisfaction** (`so.nof_solutions = solution_limit`): solutions stream to the parent,
  which drops duplicates on the declared outputs and prints up to the limit. Status:
  `timeout` if the deadline passed or Chuffed ended `unknown` (the solutions found before
  are still printed first), else `limit` when the limit was reached, else `complete`
  (some solutions) or `unsat` (none).
- **Optimisation**, phase 1 (`so.nof_solutions = 0`): branch and bound until Chuffed
  ends `finished`. **Nothing is emitted before the proof**: if the deadline passes, or
  Chuffed ends otherwise, the status is `timeout` and no solution is printed (the child
  announces the objective before solving, so even a child killed at the deadline cannot
  leak an unproven solution). A finished search with no solution is `unsat`; otherwise
  the last solution is the proven optimum and is printed. With `solution_limit == 1` the
  status is `limit`.
- Optimisation, phase 2 (only for a limit above 1): a new child runs `Build` again, posts
  `objective == optimum` (`int_rel(obj, IRT_EQ, best)`), drops the objective
  (`engine.opt_var = nullptr`) and enumerates with `so.nof_solutions = limit + 1`; the
  parent skips the optimum already printed and duplicates. Status: `limit` at the limit,
  `timeout` if the deadline passed or Chuffed did not end `finished`, else `complete`. If
  the second `Build` declares no objective the status is `error` ("Objective disappeared
  between phases").
- **Exhaustion** is Chuffed ending `finished` (search complete) with fewer solutions
  than the limit. When posting a constraint fails at the root (an infeasible model),
  Chuffed calls `exit(0)` from inside `Build`; the driver's exit hook reports that as a finished search with no
  solutions, i.e. `unsat`.
- A child that dies without reporting (a signal, e.g. 6 from a `vec` double free) is
  `error` ("Chuffed process died with signal N"); one that exits without a result is
  `error` ("Chuffed process exited without a result (code N)").
- **Time**: the driver's deadline is `max(0.1, execution_timeout - 0.3)` seconds after the
  binary starts, so `Build` (in every phase) counts. Each child gets the time left as
  `so.time_out` (at least 1 ms); at the deadline the parent `SIGKILL`s the child and
  reports `timeout`. The runner itself kills the binary at `execution_timeout` (status
  `timeout`); a nonzero exit of the binary is `error` ("C++ process exited N"). The
  evaluator maps `timeout` to `execution_timeout`, `unsat` to `no_solution` and `error`
  to `execution_error`.

## Compilation

Yes. `cpp_solver` copies the file to `/tmp/model.cpp` and runs `cmake -S /opt/cpp -B
/tmp/build -DCMAKE_BUILD_TYPE=Release` then `cmake --build /tmp/build -j1`. The project
([CMakeLists.txt](cpp/CMakeLists.txt)) builds `driver.cpp` and `/tmp/model.cpp` as C++17
into `candidate`, with `find_package(chuffed CONFIG REQUIRED)`, include directories
`/opt/cpp` and `${CHUFFED_INCLUDE_DIRS}`, linking `chuffed chuffed_fzn chuffed` (listed
twice on purpose: static library cycle), `nlohmann_json::nlohmann_json` and
`Threads::Threads`. Both steps share one budget, `compilation_timeout` (default 120 s);
running out is `compilation_error` ("Compilation timed out"), a compiler error is
`compilation_error` ("C++ compilation failed; see stderr") with the compiler output on
stderr. The binary then gets `execution_timeout`, which includes every `Build`.

## Environment

Image `dcp-eval/chuffed_cpp:v1` ([Dockerfile](Dockerfile)), on
`python:3.12.11-slim-bookworm`: g++ 12.2 (Debian `g++ 4:12.2.0-3`), make 4.3, CMake
3.25.1, nlohmann/json 3.11.2 as the JSON library (`/usr/include/nlohmann/json.hpp`),
Python 3.12.11 for the runner, and **Chuffed 0.14.0** built from the GitHub release
tarball (SHA-256 pinned) in Release mode and installed under `/opt/chuffed` (headers in
`/opt/chuffed/include/chuffed`). The image sets `CMAKE_PREFIX_PATH=/opt/chuffed`; the
CMake project the runner builds is `/opt/cpp` (with `dcp.h` and `driver.cpp`), the
runner is `/opt/runner/run.py` plus `runtime.py`. No edition or size limits.

The evaluator ([evaluation/execution.py](../../evaluation/execution.py)) runs the
container with no network, a read-only root file system, user 65534, `HOME=/tmp` and
working directory `/tmp` (a 512 MiB writable tmpfs), `/input` read-only with only
`model.cpp` and `request.json`, all capabilities dropped, at most 128 processes, and the
memory and CPU limits of the run (default 2048 MB, 1 CPU). The driver forks one child at
a time. The image's entrypoint is the runner; for an ad hoc build override it and repeat
the runner's steps:

```sh
docker run --rm --network none -v $PWD/model.cpp:/tmp/model.cpp:ro --entrypoint sh \
  dcp-eval/chuffed_cpp:v1 -c 'cmake -S /opt/cpp -B /tmp/b -DCMAKE_BUILD_TYPE=Release \
  && cmake --build /tmp/b && echo "{\"instance\": {\"n\": 2, \"optimize\": true}, \
  \"solution_limit\": 2, \"execution_timeout\": 10}" | /tmp/b/candidate'
```

The binary reads the request (`instance`, `solution_limit`, `execution_timeout`) on
stdin and prints `solution` records then one `status` record on stdout.

## Traps

- **Log to `std::cerr` only.** The binary's stdout is the runner protocol, and every
  line on it must be a JSON record (a stray line is `invalid_output`). The child's stdout
  is redirected to stderr before `Build`, but anything printed outside it is not.
- **A plain integer leaf is read as an index**, not as a value: `{"k", 5}` reports the
  value of the sixth `dcp::out` variable, or is `error` if there are fewer. A constant
  output is `dcp::out(getConstant(5))`.
- **`Build` runs in every phase**: an optimisation run with a solution limit above 1 pays
  for `Build` twice, and a `Build` that is not deterministic (random data, a different
  objective) breaks phase 2.
- **An optimum not proven within the budget emits nothing** (`execution_timeout`), even
  if good solutions were found: the proof is part of the work.
- The skill's cheat sheet says the driver "only overrides `so.vsids` after your Build":
  the driver also overrides `so.nof_solutions`, `so.print_sol` and `so.time_out`, so
  setting those in `Build` has no effect.
- Without any `branch` call, Chuffed alone would stop at the root with unfixed variables;
  here the driver's appended in-order branching fixes every integer variable, so the
  model is correct but slow. A free auxiliary does not multiply the solutions (only the
  outputs are compared), but a free *output* is enumerated over its whole domain.
- `int_mod` compiles and aborts at run time; `VAL_RANDOM` aborts at run time; `lex` on
  eager 0/1 variables crashed (signal 11); a copied `vec` double-frees (signal 6). All
  show up as `execution_error` (see the skill's pitfalls).

## Example

The pilot fixture [tests/fixtures/model_chuffed.cpp](../../tests/fixtures/model_chuffed.cpp)
(instance fields `n`, `optimize`; outputs `x`, `y`):

```cpp
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");
  IntVar* x = newIntVar(0, n);
  IntVar* y = newIntVar(0, n);
  vec<IntVar*> terms;
  terms.push(x);
  terms.push(y);
  if (instance.at("optimize").get<bool>()) {
    IntVar* total = newIntVar(0, 2 * n);
    int_linear(terms, IRT_EQ, total);
    int_rel(total, IRT_GE, n);
    optimize(total, OPT_MIN);
  } else {
    int_linear(terms, IRT_EQ, n);
  }
  outputs = {{"x", dcp::out(x)}, {"y", dcp::out(y)}};
}
```
