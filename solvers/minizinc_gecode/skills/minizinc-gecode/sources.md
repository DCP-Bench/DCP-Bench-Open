# Sources for `minizinc-gecode`

Tested with MiniZinc 2.9.3 (bundled Gecode 6.3.0), minizinc-python 0.10.0, Python 3.12.11, Debian GNU/Linux 12 (bookworm), inside a container. The skill itself is unpinned.

Existing skills: none found for MiniZinc with Gecode. The earlier integration skill this one was refactored from is the only prior text, and its solver facts are carried over here.

- <https://docs.minizinc.dev/en/2.9.3/> — MiniZinc 2.9.3 handbook: language specification, global constraints, command line, search annotations, efficiency
- <https://www.gecode.org/doc-latest/MPG.pdf> — Gecode, *Modeling and Programming with Gecode*
- <https://python.minizinc.dev/en/latest/> — minizinc-python: getting started and API reference (`Instance`, `Result`, `Status`)

Refactored from that earlier integration skill; examples verified inside the same container.

Verified by running (MiniZinc 2.9.3 and minizinc-python 0.10.0 in the image):

- Status on a time limit: no incumbent gives `UNKNOWN` and `=====UNKNOWN=====`; an incumbent on a minimise model gives `SATISFIED` with no `==========` marker.
- `all_solutions=True` and `nr_solutions=` on a `solve minimize` model raise `NotImplementedError` (`-a-o`, `-n-o`); the CLI `-a` on a minimise model prints one optimum.
- Python `all_solutions=True` counts a free auxiliary variable as a separate solution; the CLI does not repeat such a solution.
- A variable defined in its declaration (`var int: t = expr;`) is absent from `Result`; `objective` is always present for optimisation.
- `opt` is a reserved word (syntax error); `/` on integers is a type error in integer context; an unbounded `var int` under `solve maximize` reports 2147483646.
- A ragged Python list raises `TypeError: cannot determine coercion`.
- `show` flattens a 2-D array; `showJSON` nests it.
- Example outputs in `assets/` match the checks in their READMEs (nine examples now, including `assets/jobshop` and `assets/python-all-solutions`). The equal-sum split has 8 solutions and the production optimum is profit 260, both confirmed by brute force outside MiniZinc.
- The one-sided bound behaviour and the implied-constraint speed-up are the earlier integration's measured claims; a flattening regression test confirms the first, and a direct-versus-implied run on a CSPLib 049 (number partitioning) instance confirms the second (direct model times out at 25 s, implied accepted).
- `all_solutions=True` returns a list of `Solution` objects, one per solution; with no solution it is `[]` and the status is `UNSATISFIABLE`. A plain `solve` with no solution gives `result.solution` `None`.
- `result["objective"]` is present when the objective variable is named `value`; `result["value"]` raises `KeyError` when `value` is defined with `=` in its declaration.
- A `where` comprehension that selects nothing raises `EvaluationError: lower bound of empty array undefined` (a machine count above the machines in use); a guard `where exists(t in 1..T)(mach[t] = m)` removes it.
- A key that the model does not declare is accepted by minizinc-python 0.10.0 without error (`name`, `extra` tested).
- Minimising a maximum: a 5-cycle colouring with `colour[i] <= k` and `solve minimize k` gives 3; the job shop example's makespan 11 matches a brute force over all machine orders.
- CLI: `-a` on a satisfy model lists every solution then `==========`; `-a` on a minimise model prints one optimum; `-n 1` prints one solution; an unsatisfiable model prints `=====UNSATISFIABLE=====` with a model inconsistency warning; `show` on a 2-D array flattens it, `showJSON` nests it; `--time-limit 1` on a small model prints `=====UNKNOWN=====` (a 1 ms `timeout` in Python gives `UNKNOWN`).
- The Python time-limit branch `SATISFIED` (incumbent found, optimality unproven) was verified in the earlier run; the `assets/python-api` status branches are kept from that run.

## Independent toy test

An independent tester solved the toy problems of add-solver from this skill alone (no other source), using one Python model per problem. The table is the final run after repairs; the first run passed 10 of 18 (failures had one repair each, none needed a second).

| Problem | Instance | Result | First run |
|---|---|---|---|
| cryptarithm | ab-ab-aaa | PASS (infeasible) | FAIL: `all_different` without `include` |
| cryptarithm | send-more-money | PASS | FAIL: same |
| cryptarithm | two-two-four | PASS | FAIL: same |
| graph-colouring | cycle6 | PASS (2) | PASS |
| graph-colouring | k4-tail | PASS (4) | PASS |
| graph-colouring | petersen | PASS (3) | PASS |
| jobshop | ft06 | PASS (55) | FAIL: off-by-one in the machine count (own bug) |
| jobshop | small | PASS (11) | FAIL: same |
| knapsack | p01 | PASS (309) | PASS |
| knapsack | small | PASS (15) | PASS |
| knapsack-all-optimal | fourteen | PASS (9 solutions) | FAIL: `result["value"]` KeyError |
| knapsack-all-optimal | ties | PASS (5) | FAIL: same |
| knapsack-all-optimal | unique | PASS (1) | FAIL: same |
| n-queens | n3 | PASS (infeasible) | PASS |
| n-queens | n4 | PASS | PASS |
| n-queens | n8 | PASS | PASS |
| n-queens-all | n6 | PASS (4) | PASS |
| n-queens-all | n8 | PASS (92) | PASS |

**Passed: 18 of 18** (first run 10 of 18). Gaps the tester reported, and where this version covers them: ragged input and row positions (Data from Python, `assets/jobshop`); a machine subset in `disjunctive` and the empty-selection error (Modelling, Common issues); minimising a maximum (Modelling, `assets/jobshop`); `result.solution` as a list (All solutions, Solving); the objective read as `result["objective"]` (Solving, Common issues); bind only declared parameters (Data from Python).
