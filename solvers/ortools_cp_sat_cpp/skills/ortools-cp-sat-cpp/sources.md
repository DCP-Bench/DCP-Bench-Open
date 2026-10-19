# Sources for `ortools-cp-sat-cpp`

Tested with OR-Tools 9.15.6755 (C++ binary archive for Debian 12, x86_64), g++ 12.2.0, CMake 3.25.1, inside `dcp-eval/ortools_cp_sat_cpp:v1`.

Existing skills: not searched in this refactor; this skill was refactored from the DCP-Bench integration skill it replaces.

## Documentation

- <https://developers.google.com/optimization/cp/cp_solver> — CP-SAT solver guide (also as [Markdown](https://developers.google.com/optimization/cp/cp_solver.md)), the official entry point
- <https://developers.google.com/optimization/install/cpp/binary_linux> — OR-Tools C++ binary install, prerequisites and archive list
- <https://github.com/google/or-tools/releases> — release archives; the Debian 12 archive named in Install is the one tested
- <https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h> — `CpModelBuilder` API, the header the image ships; this is the reference for every builder method
- <https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.proto> — `CpSolverStatus` values
- <https://github.com/google/or-tools/blob/v9.15/ortools/sat/sat_parameters.proto> — `SatParameters` fields, including `enumerate_all_solutions`
- <https://github.com/google/or-tools/tree/v9.15/ortools/sat/samples> — official sample programs, the origin of the observer-based enumeration pattern

Dropped: the `CpModelBuilder` page at `developers.google.com/optimization/reference/sat/cp_model/CpModelBuilder`, used by earlier versions of this skill. It returned 404 on 2026-10-15 and is replaced by the header above, which returns 200 on the same date.

Dropped: the nlohmann/json 3.11.2 API page. The skill now uses nlohmann/json to read the instance file (see [Reading instance data](#reading-instance-data)); the package is `nlohmann-json3-dev` on Debian and it is present in the image.

## Verification

Every signature in this skill was checked by compiling it inside the integration image, not taken from documentation alone. The examples under `assets/` are runnable checks: `check_assets.py` runs each one and compares its output with the README's expected lines.

Checked in the image, with the evidence a reader can rerun:

- `assets/no-overlap-jobshop` prints `Makespan: 11`, which matches a brute-force search over every operation order on each machine (done in Python during the refactor). Putting all intervals into one `AddNoOverlap` call instead gives `Makespan: 23`; the Common issues row cites this.
- `AddElement` overloads are `(LinearExpr, absl::Span<const LinearExpr>, LinearExpr)` and `(LinearExpr, absl::Span<const int64_t>, LinearExpr)`. A `std::vector<IntVar>` converts to neither. `tests/ortools_cp_sat_cpp_skill_regression.py` reproduces the compile failure through the evaluator and checks that the skill documents the fix.
- `AddNoOverlap(std::vector<IntervalVar>)` and `AddCumulative` with `AddDemand` build and give the expected values in `no-overlap-jobshop` and `scheduling-cumulative`.
- Reading instance data: `nlohmann::json::parse` on a file given as `argv[1]`, linked with `find_package(nlohmann_json CONFIG REQUIRED)` and `nlohmann_json::nlohmann_json`, prints `Value: 10` for the instance in [Reading instance data](#reading-instance-data).
- Several programs from one CMake project with `foreach` and `RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin` build and run.
- `OnlyEnforceIf` reifies only in the direction it is posted: both the constraint and its negation have to be posted against the literal and its `Not()` for the indicator to be pinned. A probe in the image showed the indicator may stay false while the enforced constraint holds.
- Enumeration with auxiliary variables: a probe with an auxiliary variable not fixed by the decision variables reported 18 solutions where 6 distinct decision tuples exist. With `set_num_workers(8)` a 6-solution model reported 5. Both checked in the image.
- `MODEL_INVALID` with `ValidateCpModel` naming the variable for a domain with `lo > hi`. Checked in the image.
- `AddAllDifferent` with `std::vector<LinearExpr>` and `AddNoOverlap2D` with `NewFixedSizeIntervalVar`, `AddAutomaton` with `AddTransition`, and `AddModuloEquality` and `AddMultiplicationEquality` with bounded intermediates: checked by compiling and running probes in the image during the refactor. The probe programs are not shipped.
- Official install: the Debian 12 archive `or-tools_amd64_debian-12_cpp_v9.15.6755.tar.gz` (SHA-256 `b2c9870c8778eeb26c98742402da17da039c058fca7eca87be5c90832b04153c`) extracts to a tree where `CMAKE_PREFIX_PATH` pointing at it is enough for `find_package(ortools CONFIG)`; the examples run with `LD_LIBRARY_PATH` unset. The image sets `CMAKE_PREFIX_PATH=/opt/ortools` and `LD_LIBRARY_PATH=/opt/ortools/lib`.

Not verified, not in the skill: the earlier driver's comment that dual presolve in CP-SAT 9.11 to 9.15 can drop the optimum, and that `keep_all_feasible_solutions_in_presolve` avoids it. Nothing reproduced it, so the skill does not say it.

Open: the Install section has been run only in the image (Debian 12 archive). The download URL resolves and the checksum is the one the Dockerfile verifies, but no other platform was tested.

## Independent toy-test result

An independent tester solved the add-solver toy problems from this skill alone, with no other reference. The runner was `skills/add-solver/scripts/run_toy_tests.py` inside `dcp-eval/ortools_cp_sat_cpp:v1`, called with `--cmd '/w/models/{problem} {instance}'`. Every build and run was inside the container.

| Problem | Instances | Passed |
|---|---|---|
| cryptarithm | 3 | 3 |
| graph-colouring | 3 | 3 |
| jobshop | 2 | 2 |
| knapsack | 2 | 2 |
| knapsack-all-optimal | 3 | 3 |
| n-queens | 3 | 3 |
| n-queens-all | 2 | 2 |
| **Total** | **18** | **18** |

The tester's first-round gaps (input parsing, the image's preset CMake prefix, enumeration includes, `AddNoOverlap` signature, several programs in one CMake project) are closed in this version and in the Common issues table.
