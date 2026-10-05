# hermax: linear-expression outputs

Target: the pairs `divisible_by_1_through_9` and `fibonacci_even`, blocked as
`unsupported_value_range`. A lone hermax `IntVar` over a ten-digit range or over
0..5,333,333 is killed at the 2048 MB limit (evidence in
`generation/runs/20261001T1218Z-hermax-e024`, attempt-002 of each pair).

## What hermax produces (measured in dcp-eval/hermax:v1, hermax 1.2.5)

- A sum of variables is `hermax.model.PBExpr`; a single `c * literal` is
  `hermax.model.Term`. A PBExpr holds `terms` (coefficient, `Literal`),
  `int_terms` (coefficient, derived integer such as `DivExpr`) and `constant`.
  An `IntVar` inside a sum is lowered to its threshold literals.
- `result[PBExpr]` raises `TypeError: Unsupported decode target`.
  `result[Literal]` and `result[DivExpr]` decode.
- `constant + sum(c * result[item])` matched the value computed from decoded
  variables on 5 enumerated solutions (negated literals, subtraction, DivExpr).
- `IntVar != v` is a `Literal`; `DivExpr != v` is a `PBConstraint`, which `|`
  rejects, so a DivExpr inside an output sum cannot be blocked.
- No `%` on PBExpr or IntVar (TypeError). `number == 7 * q` works.
- Ten-digit all-different number as a digit sum: import+build+solve 0.25 s.
  40-bit sum equality: solve 0.013 s.

## Change (solvers/hermax/run.py only)

- `read(leaf, result)`: a PBExpr/Term output is summed from its decoded terms;
  integer coefficients required; anything else goes to `result[leaf]`.
- `blocking_clause`: for a PBExpr/Term output, block each summed literal (and
  each `int_terms` item whose `!=` is a Literal); a non-blockable item raises
  ValueError naming its type.
- Every output type: a solution whose declared outputs serialise identically to
  one already emitted is skipped.

## Checks

- Readiness: added `wide_output` (35 Booleans, value 2**33 + n) and
  `repeated_output_once` (a + b == 1 over 0..1 IntVars, output a + b,
  solution_limit 2, solutions_checked must be 1). All 15 checks true
  (`readiness-script.json`, `readiness-check.log`, `readiness-verify.log`).
- Negative control for the repeat guard, run directly against the image with
  the guard disabled by a mounted run.py: `{"x": 1}` emitted twice, status
  `limit`; shipped runner: once, status `complete`.
- DivExpr in an output with solution_limit 2: runner ends with status `error`
  and the ValueError message (documented in the skill).
- Re-evaluation of retained models: `reeval-summary.jsonl`, per-model output in
  `reeval/`.
- Tests: `tests-metadata.log`, `tests-container.log`.
- Skill validation: `skill-validate.log`.

## Results

Re-evaluation of 18 retained models (instance_count 99, solution_limit 2,
180 s / 180 s), three at a time:

- accepted on every instance: dudeney_numbers, session5_hardy_1729_square,
  pythagorean_triplet, session2_subset_sum, curious_set_of_integers,
  giant_cat_army, csplib_006_golomb_rulers, birthday_coins, assignment_costs,
  csplib_054_n_queens, facility_location, football, zebra, sudoku.
- execution_timeout on one instance, every other instance accepted (the CLI
  stops at the first timeout, so the rest were rerun with `--instance-ids`,
  `*.rest.json`): revenue_maximization json:2, tsp json:2 (both also timed out
  in their retained records, which were accepted with tolerate_inconclusive),
  cutting_stock json:2, knapsack json:3 (records checked only the example).
  For the last two, the pre-change runner mounted into the same image also
  times out on the first solve (`head-vs-new.log`), so the timeouts predate
  this change.

Container tests: `test_pilots` and `test_maximization` restricted to hermax,
OK. `MetadataTests`: 7 OK. Readiness verify: accepted.
