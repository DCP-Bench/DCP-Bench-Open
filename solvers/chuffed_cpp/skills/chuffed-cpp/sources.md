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
- `solvers/chuffed_cpp/cpp/dcp.h` and `solvers/chuffed_cpp/cpp/driver.cpp` in
  this repository - the submission contract: `Build`, `dcp::out`, the two-phase
  optimum-then-enumerate solve, deduplication on declared outputs, and the
  branching fallback after a model's own `branch`
- `skills/model-generator/references/acceptance.md` in this repository - the
  rule that a model opens with a problem line and comments every constraint
  group in the problem's own words

The examples in `references/examples.md` and the calls marked **(tested)** in the
cheat sheet were run through the repository evaluator against the
`dcp-eval/chuffed_cpp:v1` image on 2026-10-13. Calls marked **(header only)** come
from the header text and were not compiled.
