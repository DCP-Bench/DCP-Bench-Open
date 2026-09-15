# Sources for `ortools-cp-sat-cpp`

Documentation this skill's instructions were written from. Add an entry whenever
a claim here comes from a specific page or version.

- <https://developers.google.com/optimization/reference/sat/cp_model/CpModelBuilder> —
  `CpModelBuilder` reference, accessed 2026-09-15
- <https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h> —
  the header the image actually ships, which is authoritative over the web
  reference where the two disagree
- <https://json.nlohmann.me/api/basic_json/> — nlohmann/json 3.11.2, the JSON
  API the `instance` and `outputs` arguments use
- `solvers/ortools_cp_sat_cpp/Dockerfile` and `run.py` in this repository — the
  driver contract this skill describes, and the pinned OR-Tools 9.15.6755

Every signature in this skill was checked by compiling it inside the
integration image during the run recorded at
`generation/runs/20260915T153604-c7f2`, not taken from documentation alone.

- The `AddElement` overloads are `(LinearExpr, absl::Span<const LinearExpr>,
  LinearExpr)` and `(LinearExpr, absl::Span<const int64_t>, LinearExpr)`. A
  `std::vector<IntVar>` converts to neither; the compiler lists both as
  rejected candidates. Verified by
  `.../attempts/bales_of_hay/ortools_cp_sat_cpp/attempt-001`, which failed to
  compile, against attempt-002, which passed after converting to
  `std::vector<LinearExpr>`.
- `BoolVar::index()` is accepted as an output leaf for a declared Boolean
  output, and `BoolVar` enters `LinearExpr` arithmetic with an integer
  coefficient. Verified by the accepted `knapsack` and `capital_budget` models.
- `AddAllDifferent` and `AddMaxEquality` accept `std::vector<LinearExpr>`, which
  is what lets `csplib_054_n_queens` state its diagonals as `queens[i] - i` and
  `session2_color_simple` minimize the largest colour.
- `AddModuloEquality` and `AddMultiplicationEquality` take an `IntVar` target
  and need a bounded intermediate for each step of a longer product. Verified by
  the accepted `isbn`, `session5_grocery` and `csplib_005_autocorrelation`
  models.
- `AddAutomaton` returns an `AutomatonConstraint` whose
  `AddTransition(tail, head, label)` adds one arc, with the starting state and
  the accepting states passed to `AddAutomaton` itself. Verified by the accepted
  `csplib_012_nonogram` model across all 13 of its instances.
- `AddNoOverlap2D` with `NewFixedSizeIntervalVar` compiles and propagates.
  Verified by `csplib_009_perfect_square_placement` attempt-002.
- `OnlyEnforceIf` reifies only in the direction it is posted: both the
  constraint and its negation have to be posted against the literal and its
  `Not()` for the indicator to be pinned. This is the encoding behind every
  counting constraint in the accepted models.
