---
# Sources for `jump`

Documentation this skill's instructions were written from. Add an entry whenever
a claim here comes from a specific page or version.

Tested with JuMP 1.32.0, HiGHS.jl 1.26.0 (HiGHS 1.15.1), JSON 1.10.0, Julia 1.12.7 on Debian 12 (a Docker container on the `julia:1.12-bookworm` base).

Existing skills: none found for JuMP with HiGHS at the time of writing; the skill was written from the sources below.

- <https://jump.dev/JuMP.jl/stable/> — JuMP 1.32.0 manual: variables, constraints, containers, indicator constraints, objectives and solution queries, accessed 2026-09-30
- <https://jump.dev/JuMP.jl/stable/installation/> — installation and supported solvers
- <https://jump.dev/MathOptInterface.jl/stable/reference/standard_form/> — the MOI sets used here (AllDifferent, Table, Circuit, CountDistinct, CountBelongs, SOS1) and the bridges that reformulate them into MILP
- <https://ergo-code.github.io/HiGHS/stable/> — HiGHS options, including `mip_rel_gap`, `time_limit` and `threads`
- <https://github.com/jump-dev/HiGHS.jl> — the HiGHS.jl wrapper
- <https://github.com/JuliaIO/JSON.jl> — JSON.jl: `JSON.parsefile`, arrays parsed as vectors (`Vector{Any}` for lists of mixed values)
- <https://docs.julialang.org/en/v1/manual/variables-and-scoping/> — soft scope: assignments to a global inside a top-level loop need `global`

Verified by running: every claim about what works was checked by running Julia inside that container with HiGHS attached:

- `MOI.AllDifferent`, `MOI.Table` (with a `Float64` tuple matrix), `MOI.Circuit`, `MOI.CountDistinct`, `MOI.CountBelongs`, `SOS1`, `MOI.AllDifferent(2)` on bounded variables, and indicator constraints `b --> {...}` and `!b --> {...}` solve to OPTIMAL with the expected values.
- `MOI.AllDifferent` over affine expressions (`[q[i] + i for i in 1:n] in MOI.AllDifferent(n)`) with bounded variables is enforced: n-queens with the expression form is OPTIMAL for n = 4 and 8 with valid placements, and INFEASIBLE for n = 3.
- `MOI.AllDifferent` over unbounded integers stops with `BridgeRequiresFiniteDomainError`; `MOI.Table` with an integer matrix is rejected when the constraint is added; `MOI.Reified` has no JuMP constructor for that form; a product of two variables in a constraint is rejected as a quadratic constraint, and in the objective the status is `OTHER_ERROR`; `@constraint(model, x != y)` fails when the macro expands, naming the line.
- An infeasible model reports `INFEASIBLE` with no values; an unbounded integer objective reports `INFEASIBLE_OR_UNBOUNDED`; a time limit of 0.0001 s gives `TIME_LIMIT`; `time_limit` works as an attribute and `set_time_limit_sec` as a call.
- Integer variables come back as `Float64`; `permutedims(reduce(hcat, rows))` makes a `Matrix` from a list of rows; `div` gives integer division and `/` a float.
- JSON 1.10.0 is in the image's project (`JULIA_PROJECT=/opt/jump`); a Julia session without that project fails with `Package JSON not found in current path`.
- In a script, a top-level `while` block that reassigns a global (`i += 1`, `count += 1`) fails with `UndefVarError` and a soft-scope warning; declaring the variable `global` inside the block fixes it.
- Ragged jobs (lengths 2 and 3) work with one vector per job, sized from each job's own length.
- Graph colouring (colour classes, `mip_rel_gap` 0) proves 3 colours for a 5-cycle with a pendant node; the SEND + MORE = MONEY cryptarithm has the unique digits D=7 E=5 M=1 N=6 O=0 R=8 S=9 Y=2.
- Every example in `assets/` prints the stated Expected lines under `julia model.jl` in the image (checked with `check_assets.py`).

Independent toy-test result (a tester that had only the skill, with no access to the examples; models and results kept in the refactor workspace, run with `run_toy_tests.py --timeout 300` in the image):

| Family | Instances | Passed |
|---|---|---|
| cryptarithm | 3 | 3 |
| graph-colouring | 3 | 3 |
| jobshop | 2 | 2 |
| knapsack | 2 | 2 |
| knapsack-all-optimal | 3 | 3 |
| n-queens | 3 | 3 |
| n-queens-all | 2 | 2 |
| **Total** | **18** | **18/18** |

The first run was 17/18: the jobshop model assumed equal operation counts per job, which the skill then did not warn about. The skill now covers ragged input, JSON reading, output formatting, the top-level scoping trap and all-different over expressions, the points the tester raised.

Refactored from an earlier integration skill; examples verified inside the same container.
