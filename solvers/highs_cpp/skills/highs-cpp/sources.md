# Sources for `highs-cpp`

Tested with HiGHS 1.15.1 (commit 04024d701f79feb8e2f18bc3df0dffc04ef05088), C++17, g++ 12.2.0, CMake 3.25, Debian 12 (bookworm).

Existing skills: none found in the HiGHS repository tree or in this repository's skill folders. The skills.sh registry was not searched (no `npx skills find` run during setup).

- https://github.com/ERGO-Code/HiGHS (tag v1.15.1, MIT) — the C++ API (`highs/Highs.h`), status enums (`highs/lp_data/HConst.h`), option names and defaults (`highs/lp_data/HighsOptions.h`), the C++ interface guide (`docs/src/interfaces/cpp/library.md`, `examples.md`), the example `examples/call_highs_from_cpp.cpp`, and the CMake install layout (`highs-config`, target `highs::highs`).

Verified by running: install commands and build of the Quick start with v1.15.1 in a Debian bookworm image; every example in `assets/` compiled and printed its Expected line; statuses `Optimal`, `Infeasible`, `Unbounded or infeasible`, `Empty`, `Not Set` on a 0.2 s time limit; default option values `time_limit` inf, `mip_rel_gap` 1e-4, `mip_abs_gap` 1e-6, `mip_feasibility_tolerance` 1e-6, `threads` 0, `random_seed` 0, `output_flag` true; `getInfo().objective_function_value` includes the objective offset; columns up to 5e9 keep their values.
