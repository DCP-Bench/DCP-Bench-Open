# Sources for `chuffed-cpp`

Documentation this skill's instructions were written from. Add an entry whenever
a claim here comes from a specific page or version.

Chuffed 0.14.0 is tag `0.14.0`, commit `f698d5623bb0c2bcd497388ba966f0436d62caf4`.
Raw files are served at `https://raw.githubusercontent.com/chuffed/chuffed/0.14.0/`.

- <https://github.com/chuffed/chuffed/tree/0.14.0/chuffed/examples> - the 25
  official C++ examples (`queens.cpp`, `golomb.cpp`, `rcpsp.cpp`,
  `concert_hall.cpp`, `non.cpp`, `shift.cpp`, `grid_colouring.cpp`, ...), source
  of the usage patterns and of which calls have an official example
- <https://raw.githubusercontent.com/chuffed/chuffed/0.14.0/chuffed/primitives/primitives.h> -
  `int_rel`, `int_linear`, reification, arithmetic, element, `bool2int`,
  `bool_rel`, `bool_clause`, `array_bool_*`, `IntRelType`, `BoolRelType`
- <https://raw.githubusercontent.com/chuffed/chuffed/0.14.0/chuffed/globals/globals.h> -
  `all_different*`, `inverse`, `circuit`, `table`, `regular`, `lex`,
  `disjunctive`, `cumulative*`, `minimum`, `maximum`, `bool_linear`, graph globals
- <https://raw.githubusercontent.com/chuffed/chuffed/0.14.0/chuffed/vars/modelling.h> -
  `createVar`, `createVars`, `flatten`, `transpose`
- <https://raw.githubusercontent.com/chuffed/chuffed/0.14.0/chuffed/vars/int-var.h> -
  `newIntVar`, `getConstant`, `getLit`, literal operators, domain limits
- <https://raw.githubusercontent.com/chuffed/chuffed/0.14.0/chuffed/vars/bool-view.h> -
  `BoolView`, `operator~`, `newBoolVar`, `bv_true`, `bv_false`
- <https://raw.githubusercontent.com/chuffed/chuffed/0.14.0/chuffed/branching/branching.h> -
  `branch`, `VarBranch`, `ValBranch`, `BranchGroup`
- <https://raw.githubusercontent.com/chuffed/chuffed/0.14.0/chuffed/core/engine.h> -
  `optimize`, `OPT_MIN`, `OPT_MAX`, `engine`
- <https://raw.githubusercontent.com/chuffed/chuffed/0.14.0/chuffed/support/vec.h> -
  `vec<T>` and its element-converting constructor
- <https://github.com/CPMpy/cpmpy/pull/1100> - head commit
  `4b1a9dd982982ada53ed0f6b9f32c9ceb6748859`, CPMpy's in-progress agent skill
  (`skills/cpmpy-model/SKILL.md`, `references/api-cheatsheet.generated.md`),
  borrowed for the layout: a short routing SKILL.md, a one-bullet-per-call cheat
  sheet with constraint tables, tips, and a full toy example
- <https://agentskills.io/specification> - the Agent Skills format
- <https://github.com/chuffed/chuffed> (README, `LICENSE`) - source build with CMake, MIT
  licence; the C++ library is only available by building from source
- <https://github.com/nlohmann/json> - the JSON library of the `graph-colouring-json`
  example (`json::parse`, `.at`, `.get<T>()`, `.value(key, default)`, CMake target
  `nlohmann_json::nlohmann_json`)
- A model-acceptance checklist for generated models - the
  rule that a model opens with a problem line and comments every constraint
  group in the problem's own words (kept here as the *Style* rule)

Earlier verification (kept as provenance): earlier versions of the queens, knapsack and
recipe programs, written for an evaluator's driver interface, and the calls marked
**(tested)** in the cheat sheet were run against a Chuffed 0.14.0 Linux container
image on 2026-10-13. Calls marked **(header only)** come from the header text and were not
compiled.

Added for standalone use:

- `chuffed/core/engine.h`, `chuffed/core/options.h` (0.14.0, installed headers) - `Problem`,
  `so.nof_solutions`, `so.time_out`, `so.print_sol`, `engine.status`, `RES_*`,
  `engine.solutions`, `engine.best_sol`, `setSolutionCallback`
- `chuffed/examples/template.cpp` and `queens.cpp` (0.14.0) - standalone program shape
  (`Problem` subclass, `output_vars`, `parseOptions`, `engine.solve(new P(...))`); the
  `queens` example is based on `queens.cpp`
- A Debian 12 `Dockerfile` and a `CMakeLists.txt` for Chuffed 0.14.0 (not part of this
  skill) - verified source build (release tarball, `cmake -DCMAKE_BUILD_TYPE=Release`,
  `cmake --install`), install prefix and link line (`find_package(chuffed CONFIG REQUIRED)`,
  `chuffed chuffed_fzn chuffed`, Threads)
- `standalone_queens.cpp` and `standalone_knapsack.cpp` (now `assets/queens/model.cpp` and
  `assets/knapsack-maximise/model.cpp`) were compiled and run in the image on 2026-10-13:
  `queens 8`, `queens 6 0` (4 solutions), `queens 3 5` (unsatisfiable), `knapsack`
  (optimum 51). Without `output_vars`, enumeration stops after the first solution.
- An earlier integration driver for Chuffed - where the two-phase all-optimal pattern
  (optimum in a forked child, then a fresh build with the objective fixed) and the
  per-phase `fork()` around Chuffed's non-resettable globals were first worked out.
- The search and performance lessons in `references/performance.md` and the pitfalls in
  *Common issues* come from campaigns of several hundred generated Chuffed models;
  timings were measured there.

Refactored from an earlier integration skill; examples verified with Chuffed 0.14.0
(g++ 12.2, CMake 3.25.1, nlohmann/json 3.11.2, Debian 12, 2026-10-16).

Verified by running (2026-10-16, in a Debian 12 container with Chuffed 0.14.0):

- every example in `assets/` with `check_assets.py` (8/8 pass) and the Quick start;
- optimisation ends with `RES_LUN` and ignores `so.nof_solutions = 1`; a complete
  satisfaction search ends with `RES_GUN`, also with 0 solutions (`queens 3 0`);
- a failure at the root (posting `x >= 5` on 0..3, or pigeonhole `all_different`) prints
  `=====UNSATISFIABLE=====` and `% Top level failure!` on stdout and calls `exit(0)`
  before `engine.solve` returns, with `engine.status` still `RES_SAT` in an `atexit`
  handler;
- `==========` and `=====UNSATISFIABLE=====` are printed with `so.print_sol = false`, and
  the solution callback runs either way;
- Booleans that no `branch` reaches are reported unfixed (read 0, breaking
  `bool_linear(bs, IRT_GE, 2)`), also with `so.vsids = true`;
- `so.vsids = true; engine.branching->add(&sat);` after the model's `branch` calls fixes
  those Booleans (the same call the integration driver uses);
- the optima of `project-schedule` (11) and `make-change-all-optimal` (2 coins, 3 ways)
  were checked by brute force.
- a `Problem` subclass without `print` fails to compile with "invalid new-expression of
  abstract class type" (`Problem::print` is pure virtual); with an empty `print` it builds;
- the one-printed-optimum snippet: the solution callback ran 3 times on the knapsack model
  (`so.print_sol = false`), the last values were the optimum 51.

Existing skills: none found for Chuffed's C++ API when the skill was first written
(CPMpy's in-progress skill above was used for layout only).

Independent toy test: 18/18
