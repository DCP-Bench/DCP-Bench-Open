# gecode_cpp: how this integration realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how Gecode in
C++ expresses it. Runner: [run.py](run.py), which calls `main("cpp")` in
[runner/runtime.py](../../runner/runtime.py) (`cpp_solver`). That compiles the submission
together with the driver [cpp/driver.cpp](cpp/driver.cpp) and the header
[cpp/dcp.h](cpp/dcp.h) (the `dcp::Space` base class) using
[cpp/CMakeLists.txt](cpp/CMakeLists.txt), then runs the binary, which owns `main`,
solving, enumeration and printing. The solver skill
([skills/gecode-cpp/SKILL.md](skills/gecode-cpp/SKILL.md)) covers the Gecode API with
standalone programs (own `main`, `DFS`/`BAB`, printing); [Example](#example) below shows
how one becomes a submission, with a complete optimisation submission (row seating).

## Submission file

One C++17 source file, `model.cpp`, compiled as a second translation unit next to
`driver.cpp`. It starts with `#include "dcp.h"`, which includes `<gecode/int.hh>`,
`<gecode/minimodel.hh>`, `<gecode/search.hh>`, `<gecode/set.hh>`, `<nlohmann/json.hpp>`,
`<cstddef>`, `<stdexcept>`, `<string>`, `<vector>`, and declares `using namespace
Gecode; using nlohmann::json;`. Include anything else yourself (`<gecode/float.hh>` is
linked but not included). The file defines **one class derived from `dcp::Space`** and
ends with **`DCP_MODEL(ClassName)`**; it has **no `main`** and runs no search itself.

## Entrypoint

`DCP_MODEL(M)` defines the function the driver calls:

```cpp
dcp::Space* dcp_make(const json& instance);   // DCP_MODEL(M): return new M(instance);
```

so the class needs:

```cpp
class M : public dcp::Space {
 public:
  explicit M(const json& instance);                 // post the whole model here
  M(M& s) : dcp::Space(s) { /* x.update(*this, s.x) for every member */ }
  Gecode::Space* copy() override { return new M(*this); }
};
DCP_MODEL(M)
```

- **Constructor** `explicit M(const json& instance)`, also when the instance has no
  fields (then `(void)instance;`, with the constants from the description written in
  the constructor and commented). Sizes come from the data, so create member arrays in
  the body: `x = IntVarArray(*this, n, lo, hi)`. The driver constructs the model once.
- **Copy constructor** `M(M& s) : dcp::Space(s)` updates every member variable
  (`IntVarArray`, `IntVar`, `BoolVar*`, `SetVar*`); `copy()` returns `new M(*this)`.
  `dcp::Space` copies the registered outputs, the objective and the restart scale
  itself.
- Derive from `dcp::Space`, not from `IntMinimizeSpace`/`IntMaximizeSpace`, and do not
  override `constrain`: `dcp::Space` implements it for its own objective.

## Instance

`instance` is the request's `instance` object as an `nlohmann::json`, 0-based. Read data
with `instance.at("n").get<int>()`, `std::vector<int> w = instance.at("w")`,
`instance.at("m")[i][j].get<int>()`, JSON Booleans with `.get<bool>()`. Ragged arrays are
ordinary nested arrays: a field the brief calls unbindable (ragged rows, mixed types) is
still readable here from the JSON. The brief's shapes are those of its example instance;
take every size, output lengths included, from `instance`. A missing field
(`instance.at` throws) or any other exception from the constructor becomes status
`error` with the exception message as detail.

## Outputs

Register each declared output in the constructor with the protected
**`output("name", v)`**, once per name the brief declares and no others (an extra name,
such as the objective when it is not declared, is `invalid_output`; a name registered
twice throws, status `error`). `v` may be:

| Value | Reported as |
|---|---|
| `IntVar`, `BoolVar` | a scalar (a `BoolVar` as `0`/`1`) |
| `IntVarArray` / `IntVarArgs`, `BoolVarArray` / `BoolVarArgs` | a list |
| `std::vector<IntVarArgs>`, `std::vector<BoolVarArgs>` | a list of lists (one inner list per element) |
| `Matrix<IntVarArray>` / `Matrix<IntVarArgs>`, `Matrix<BoolVarArray>` / `Matrix<BoolVarArgs>` | a list of rows: outer index is the row, `m(c, r)` is column `c` of row `r` |
| `std::vector<std::vector<IntVarArgs>>` (or `BoolVarArgs`) | three levels of lists |
| `int`, `std::vector<int>` | the constant(s), unchanged |

- **Wide values**: a number beyond the `IntVar` range (±(2^31 − 2)) is
  **`output_digits("name", digits, base)`** (`base` defaults to 10) with digit variables
  `IntVarArgs digits`, most significant first; the driver reports
  `Σ digits[i]·base^(n−1−i)` as a 64-bit integer.
- A derived value (a sum, a count) is an output through an `IntVar` made with `expr`
  (`total = expr(*this, sum(x))`).
- Every output variable must be assigned at a solution; an unassigned one is status
  `error` ("output NAME is not assigned: branch on it"). The driver's fallback branching
  (below) assigns every registered variable, so this arises only in odd cases.
- No outputs registered at all is `error` ("Expected output dictionary").

## Objective

Call the protected **`minimize(v)`** or **`maximize(v)`** once in the constructor, on an
`IntVar` (`total = expr(*this, sum(...))`), in the direction the brief gives; a second
call throws (`error`). Export it with `output(...)` only if it is a declared output. No
call for a satisfaction problem. Do not bound it with a value known from elsewhere.

**Restarts** (optional): `restarts(scale)`, e.g. `restarts(100)`, makes the driver search
with Luby restarts of that scale (still complete, since the cutoff grows without bound).
Pair it with AFC or CHB branching. It is not a default: it can slow the optimality proof.

## Solving

The driver ([driver.cpp](cpp/driver.cpp)) builds the model once by `dcp_make`, then:

- If the root space fails on propagation (`status() == SS_FAILED`), the status is
  `unsat`.
- It posts a **fallback branching after the model's own `branch` calls**:
  `INT_VAR_SIZE_MIN()`, `INT_VAL_MIN()` over every registered integer output variable
  (digit variables included) and the objective, then `BOOL_VAR_NONE()`,
  `BOOL_VAL_MIN()` over every registered Boolean output. Auxiliary variables are not
  branched on: branch on all your decision variables yourself.
- Every search runs on **one thread** (`threads = 1`) with a `Search::TimeStop` set to
  the milliseconds left before the deadline, plain `DFS`/`BAB`, or `RBS<…, DFS>` /
  `RBS<…, BAB>` with `Search::Cutoff::luby(scale)` when the model called
  `restarts(scale)`. Other search options keep Gecode's defaults; the model cannot change
  any of this.
- **Satisfaction**: solutions are found one at a time. For each, the driver clones the
  root, posts for every solution found so far a no-good that at least one registered
  output variable (integer or Boolean) differs from its value there (`clause(BOT_OR,
  ...)` over reified `IRT_NQ`), and runs a fresh DFS from that root. So every solution
  after the first is a new search from the root with the earlier ones forbidden, and it
  must come quickly too. Distinctness is on the declared outputs only; auxiliaries are
  not compared.
- **Optimisation**: branch and bound (`BAB`, or `RBS<…, BAB>` with restarts) on a clone
  of the root until the search ends. `dcp::Space::constrain` posts a **strict**
  improvement bound on the objective at every node: `objective < incumbent` when
  minimising, `objective > incumbent` when maximising. (Before commit `bd71fbf69` the
  minimisation bound was `objective < incumbent − 1`, which skipped a solution exactly
  one better than the incumbent; readiness check `optimum_one_below_first` covers it.)
  **Nothing is emitted before the proof**: a search stopped by the time limit is
  `timeout`, with no solution; a search that ends with no solution is `unsat`;
  otherwise the last solution is the proven optimum. With `solution_limit == 1` it is
  printed with status `limit`. Otherwise the driver clones the root, posts
  `objective == optimum`, forbids the optimum with the no-good above, and enumerates
  further optimal solutions as for satisfaction.
- **Statuses**: the solutions found are printed together at the end, then one status:
  `limit` when the solution limit is reached; `complete` (some solutions) or `unsat`
  (none) when a search ends without being stopped (exhaustion); `timeout` when a search
  was stopped by the time limit or the deadline had passed (solutions found before are
  still printed, except in the branch and bound phase); `error` for any exception
  (`dcp_make`, an unassigned output, a duplicate name), with its message as detail. A
  propagator still alive at a solution is only noted on stderr ("note: N propagators
  not subsumed at solution").
- **Time**: the driver's deadline is `max(0.1, execution_timeout - 0.3)` seconds after
  the binary starts, so the constructor counts; each search gets what is left. The
  runner kills the binary at `execution_timeout` (status `timeout`, and then nothing
  the driver found is printed); a nonzero exit (a crash) is `error` ("C++ process exited
  N"). The evaluator maps `timeout` to `execution_timeout`, `unsat` to `no_solution` and
  `error` to `execution_error`.

## Compilation

Yes. `cpp_solver` copies the file to `/tmp/model.cpp` and runs `cmake -S /opt/cpp -B
/tmp/build -DCMAKE_BUILD_TYPE=Release` then `cmake --build /tmp/build -j1`. The project
([CMakeLists.txt](cpp/CMakeLists.txt)) builds `driver.cpp` and `/tmp/model.cpp` as C++17
into `candidate`, include directory `/opt/cpp`, linking `gecodesearch gecodeminimodel
gecodeset gecodefloat gecodeint gecodekernel gecodesupport`,
`nlohmann_json::nlohmann_json` and `Threads::Threads`. Both steps share one budget,
`compilation_timeout` (default 120 s); running out is `compilation_error` ("Compilation
timed out"), a compiler error is `compilation_error` ("C++ compilation failed; see
stderr") with the build log on stderr. Every evaluation run compiles the model first.
The binary then gets `execution_timeout`, which includes the constructor.

## Environment

Image `dcp-eval/gecode_cpp:v1` ([Dockerfile](Dockerfile)), on
`python:3.12.11-slim-bookworm`: g++ 12.2 (Debian `g++ 4:12.2.0-3`), make 4.3, CMake
3.25.1, nlohmann/json 3.11.2 as the JSON library (`/usr/include/nlohmann/json.hpp`),
**Gecode 6.2.0** from Debian `libgecode-dev 6.2.0-5` (headers in `/usr/include/gecode`,
libraries on the system library path, so no `CMAKE_PREFIX_PATH` or `LD_LIBRARY_PATH` is
needed), Python 3.12.11 for the runner. The CMake project the runner builds is
`/opt/cpp` (with `dcp.h` and `driver.cpp`), the runner is `/opt/runner/run.py` plus
`runtime.py`. No edition or size limits.

The evaluator ([evaluation/execution.py](../../evaluation/execution.py)) runs the
container with no network, a read-only root file system, user 65534, `HOME=/tmp` and
working directory `/tmp` (a 512 MiB writable tmpfs), `/input` read-only with only
`model.cpp` and `request.json`, all capabilities dropped, at most 128 processes, and the
memory and CPU limits of the run (default 2048 MB, 1 CPU). The image's entrypoint is the
runner; for an ad hoc build override it and repeat the runner's steps:

```sh
docker run --rm --network none -v $PWD/model.cpp:/tmp/model.cpp:ro --entrypoint sh \
  dcp-eval/gecode_cpp:v1 -c 'cmake -S /opt/cpp -B /tmp/b -DCMAKE_BUILD_TYPE=Release \
  && cmake --build /tmp/b && echo "{\"instance\": {\"n\": 2, \"optimize\": true}, \
  \"solution_limit\": 2, \"execution_timeout\": 10}" | /tmp/b/candidate'
```

The binary reads the request (`instance`, `solution_limit`, `execution_timeout`) on
stdin and prints `solution` records then one `status` record on its stdout (the
process's own `std::cout` goes to stderr).

## Traps

- **Printing does not reach the protocol, but it is not shown as output either.** The
  driver writes its records to a private copy of stdout and points `std::cout` and
  `printf` at stderr, so a model's own printing ends up in the log only. Values are
  reported through `output(...)` alone.
- **An auxiliary that no branching and no propagation fixes can give a wrong
  solution**: Gecode reports a solution once every brancher is done, and the fallback
  branching covers only the outputs and the objective. The outputs are then reported
  although no value of the open auxiliary may extend them, and the evaluator rejects the
  solution (`invalid_solution`). Branch on every decision variable.
- **Forgetting a member in the copy constructor** compiles and then reads garbage or
  crashes (`execution_error`). The outputs themselves are safe (`dcp::Space` keeps its
  own copies), the constraints on the forgotten member are not.
- Never keep an `IntVarArgs` as a member to read later: it is not updated on copy.
- `output_digits` reads the digits into a 64-bit integer without checking the range, and
  the no-good compares digit variables, so give each digit the domain `0..base−1`.
- A constant output (`output("k", 5)`) does not distinguish solutions; if every output
  is a constant, the first solution exhausts the search.

## Example

The pilot fixture [tests/fixtures/model_gecode.cpp](../../tests/fixtures/model_gecode.cpp)
(instance fields `n`, `optimize`; outputs `x`, `y`):

```cpp
#include "dcp.h"

class Model : public dcp::Space {
  IntVarArray v;
 public:
  explicit Model(const json& instance) : v(*this, 2, 0, instance.at("n").get<int>()) {
    int n = instance.at("n");
    IntVarArgs xy(2);
    xy[0] = v[0];
    xy[1] = v[1];
    if (instance.at("optimize").get<bool>()) {
      linear(*this, xy, IRT_GQ, n);
      IntVar total(*this, 0, 2 * n);
      IntVarArgs all(3);
      all[0] = v[0];
      all[1] = v[1];
      all[2] = total;
      linear(*this, IntArgs({1, 1, -1}), all, IRT_EQ, 0);
      minimize(total);
    } else {
      linear(*this, xy, IRT_EQ, n);
    }
    branch(*this, v, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("x", v[0]);
    output("y", v[1]);
  }
  Model(Model& s) : dcp::Space(s) { v.update(*this, s.v); }
  Gecode::Space* copy() override { return new Model(*this); }
};
DCP_MODEL(Model)
```

### From a standalone Gecode program to a submission

The skill's examples are standalone programs. To turn one into a submission:

| Standalone program | Submission |
|---|---|
| `#include <gecode/...>`, `using namespace Gecode;` | `#include "dcp.h"` (includes them and nlohmann JSON) |
| `class M : public Space` / `IntMinimizeSpace` / `IntMaximizeSpace` | `class M : public dcp::Space` |
| data inline or read from a file in `main` | `explicit M(const json& instance)`, data from `instance` |
| `IntVar cost() const override` and `BAB<M>` | `minimize(total)` / `maximize(total)` in the constructor |
| `RBS<M, BAB>` with `Search::Cutoff::luby(100)` | `restarts(100)` in the constructor |
| `int main()` with the search loop, `print()` | none: `output("name", v)` per declared output, then `DCP_MODEL(M)` |
| copy constructor `M(M& s) : Space(s)`, `Space* copy()` | `M(M& s) : dcp::Space(s)`, `Gecode::Space* copy() override` |

### Row seating (an optimisation submission)

Outputs `seat` and `total`; instance fields `n`, `preferred`, `enemies`:

```cpp
#include "dcp.h"

// Row seating: seat n guests in a row of n chairs so that no two enemies sit side
// by side, and minimise the total distance from each guest's preferred chair.
class Seating : public dcp::Space {
 protected:
  IntVarArray seat;   // seat[g]: chair of guest g
  IntVarArray guest;  // guest[c]: guest on chair c
  IntVar total;

 public:
  explicit Seating(const json& instance) {
    int n = instance.at("n");
    std::vector<int> preferred = instance.at("preferred");
    seat = IntVarArray(*this, n, 0, n - 1);
    guest = IntVarArray(*this, n, 0, n - 1);

    // every chair holds exactly one guest
    channel(*this, seat, guest, IPL_DOM);

    // enemies never sit side by side
    for (const auto& pair : instance.at("enemies"))
      rel(*this, abs(seat[pair[0].get<int>()] - seat[pair[1].get<int>()]) >= 2);

    // minimise the total distance from the preferred chairs
    IntVarArgs distance;
    for (int g = 0; g < n; ++g) distance << expr(*this, abs(seat[g] - preferred[g]));
    total = expr(*this, sum(distance));

    branch(*this, seat, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    minimize(total);
    output("seat", seat);
    output("total", total);
  }

  Seating(Seating& s) : dcp::Space(s) {
    seat.update(*this, s.seat);
    guest.update(*this, s.guest);
    total.update(*this, s.total);
  }
  Gecode::Space* copy() override { return new Seating(*this); }
};

DCP_MODEL(Seating)
```

Two larger submissions of the same shape are the skill's
[json-roster](skills/gecode-cpp/assets/json-roster/model.cpp) (registers
`output("roster", m)` on the `Matrix` and `output("total", total)`; proven optimum 36 in
0.1 s through the driver) and
[scheduling-machines-crew](skills/gecode-cpp/assets/scheduling-machines-crew/model.cpp)
(`restarts(100)`, outputs `start`, `machine`, `makespan`; optimum 8 in under 0.01 s),
converted with the table above.

