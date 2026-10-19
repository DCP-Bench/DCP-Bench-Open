# Sources for `gecode-cpp`

Tested with Gecode 6.2.0 (Debian bookworm `libgecode-dev 6.2.0-5`), g++ 12.2.0, C++17,
nlohmann/json 3.11.2.

Existing skills: not searched.

Independent toy test: 18/18.

## Documentation

- Gecode 6.2.0 as packaged by Debian bookworm, `libgecode-dev=6.2.0-5`
  (<https://packages.debian.org/bookworm/libgecode-dev>). Upstream tag `release-6.2.0`,
  <https://github.com/Gecode/gecode/tree/release-6.2.0>. Licence: MIT-style Gecode licence.
- The installed headers `/usr/include/gecode/{int,set,minimodel,search}.hh` and
  `gecode/int/*.hh`: every signature in `references/constraints.md` was extracted from
  them.
- Christian Schulte, Guido Tack, Mikael Z. Lagerkvist, *Modeling and Programming with
  Gecode*, version for Gecode 6.2.0 (<https://www.gecode.org/doc-latest/MPG.pdf>):
  Space, cloning, MiniModel, propagation levels, branching, search engines, LDSB.
- API reference 6.2.0, <https://www.gecode.org/doc/6.2.0/reference/>: the group and
  class pages linked from SKILL.md (all returned 200 on 2026-10-16).
- <https://www.gecode.org/download.html>, <https://formulae.brew.sh/formula/gecode>:
  install routes other than Debian (not tested).
- Gecode's own examples, <https://github.com/Gecode/gecode/tree/release-6.2.0/examples>:
  `money.cpp` and `queens.cpp` are the origin of the satisfy and all-solutions examples.
- nlohmann/json, <https://json.nlohmann.me/>: reading the JSON data file.

## Verification

- `references/catalogue.cpp` checks the semantics stated in SKILL.md against brute
  force (51 checks, all passing on Gecode 6.2.0, rerun in this refactor).
- The nine examples under `assets/` pass `check_assets.py` (compile and run) on
  Gecode 6.2.0. Optima were checked independently: seating 8 against all 720
  permutations, knapsack 41 against all 64 subsets, makespan 8 equals the work bound,
  queens 92 is the known count, ft06 makespan 55 is the published optimum.
- The Quick start was extracted from SKILL.md, compiled and run: `Profit: 12 at x = 4, y = 0`.
- Unbranched auxiliaries: a probe with three 0..1 variables under `distinct` (default
  level) and no branching on them reported 4 "solutions" of an infeasible model, the
  variables unassigned (`IntVar::val: Attempt to access value of unassigned variable`)
  and one propagator alive.
- An uncaught `Int::OutOfLimits` prints `terminate called after throwing an instance
  of 'Gecode::Int::OutOfLimits'` / `what(): IntVar::IntVar: Number out of limits` and
  exits 134; `Int::Limits::max` is 2147483646.
- `INT_VAR_REGRET_MIN_MAX`, `INT_VAL_SPLIT_MIN`, `Search::Stop::node`,
  `engine.statistics()` and `VariableSymmetry` compile and run (probe).
- The modelling and search lessons (branching styles, implied prefix bounds, partial
  sums over grids, products, restarts against in-order search, timings) come from
  a few hundred Gecode models written for a benchmark of constraint problems.
