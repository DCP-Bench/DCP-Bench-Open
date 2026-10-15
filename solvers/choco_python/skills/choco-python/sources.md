# Sources for `choco-python`

Tested with pychoco 0.2.1 and 0.4.0 (Choco bundled in each wheel), Python 3.12.11, inside the Linux
image `dcp-eval/choco_python:v1`. Every example passes on both versions; 0.4.0 was installed into a
scratch directory in the same image for the comparison.

Refactored from the DCP-Bench integration skill; examples verified inside the dcp-eval/choco_python:v1 image.

- <https://pychoco.readthedocs.io/en/latest/> — pychoco reference, accessed 2026-09-16
- <https://pypi.org/project/pychoco/> — the wheels tested (0.2.1, 0.4.0); each bundles the Choco native library, so no JVM is needed
- <https://choco-solver.org/docs/> — Choco 4 solver documentation, for the meaning of the constraints pychoco exposes
- <https://github.com/chocoteam/pychoco> — pychoco source

## Independent toy-problem test

An independent agent wrote one program per toy problem from this skill alone (no access to the
examples or the solver source), Python 3.12.11 with pychoco 0.2.1 in the image. Runner output:
`scratchpad/skill-refactor/choco_python/test/results.txt` (during the refactor).

| Problem | Instances | Passed |
|---|---|---|
| cryptarithm | 3 (ab-ab-aaa, send-more-money, two-two-four) | 3/3 |
| graph-colouring | 3 (cycle6, k4-tail, petersen) | 3/3 |
| jobshop | 2 (ft06, small) | 2/2 |
| knapsack | 2 (p01, small) | 2/2 |
| knapsack-all-optimal | 3 (fourteen, ties, unique) | 3/3 |
| n-queens | 3 (n3, n4, n8) | 3/3 |
| n-queens-all | 2 (n6, n8) | 2/2 |
| **Total** | **18** | **18/18** |

All 18 passed on the first run, so no repair was needed. The gaps the tester reported (JSON I/O,
distinct-value counting, no-overlap, `arithm` forms, `scalar` with repeated variables, `Solution` access)
are now covered in SKILL.md. The tester did not execute the skill's example files; those are checked separately.

## Verified by running (inside the image)

- Method names: `sum`, `min`, `max` exist; `sum_`, `min_` do not; `and_`, `or_`, `not_` exist.
- `element(value, table, index)` gave pairs (5,0), (7,1), (9,2) for table [5, 7, 9]; `max(r, [a, b])` gives the maximum.
- `find_solution` and `find_optimal_solution` return `None` when infeasible; `find_all_solutions` and
  `find_all_optimal_solutions` return `[]`; `solve()` returns `False`.
- A second solve on one model after an infeasible result (any `get_solver()`) ends the process with a JVM
  "Fatal error", exit code 99; a new `Model` for the second solve works.
- `find_all_optimal_solutions` returns both optima of a tie (choose-two example).
- A posted vs. unposted constraint: with `x + y >= 1` posted and `arithm(x, "=", 2)` left unposted, 15
  solutions; Choco prints `ARITHM ([x = 2]) is free` on stdout.
- Free auxiliary variables multiply enumerated solutions: 12 for 2 outputs with a free `aux` in 0..5, 2 when
  `aux = x`.
- `limit_time`: `"0.5s"` honoured (0.80 s on a 10^6-solution enumeration); `"300ms"` ignored (2.87 s, full run);
  `"2s"` stopped the enumeration around 2.6 s. (Earlier measurement: a 10 million enumeration with `"300ms"`
  ran to completion, 40 s.)
- Operators: `x + y == 3` returns a BoolVar with no `post` method; `model.arithm(x + y, "=", 3)` gives 4 solutions for x, y in 0..3.
- `arithm(q, "+", 2, "=", up)` (int middle value) gives the correct pairs; `arithm(2, "<=", q)` raises
  `AttributeError` (an int on the left).
- `cumulative` with int heights or capacity raises `AttributeError`; with IntVars it works.
- No-overlap: three tasks of length 2 on one unit-capacity `cumulative` gave 6 solutions, none overlapping.
- `scalar` with a repeated variable (`[x, x]`, `[1, 2]`, `= 3`) and with mixed signs matches a brute-force count (15 solutions).
- `Solution`: `get_int_val` and `get_set_val` exist, `get_value` does not; a `Solution` keeps its values after a
  later solve; `var.get_value()` after `find_all_solutions` raises `AssertionError: ... not instantiated`.
- Scheduling: `model.task(start, duration, end)` and `model.cumulative(tasks, heights, capacity)` gave makespan 9,
  matching an independent brute force, on both 0.2.1 and 0.4.0 without any extra call.
- `ensure_bound_consistency()` exists on `Task` in 0.2.1 and is absent in 0.4.0; no example calls it.
- Transport and production optima (240, 17) checked against an independent brute force and by hand.
- Distinct-value count: the 5-node graph with a triangle gives 3 colours (distinct-count example).
- Knapsack instance in `json-io` (weights 3, 4, 2, 5; values 7, 9, 4, 8; capacity 9) gives profit 20 (items 0, 1, 2).
