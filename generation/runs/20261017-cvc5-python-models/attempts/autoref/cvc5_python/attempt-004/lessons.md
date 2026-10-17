# autoref, cvc5_python: lessons from the free checks

No attempt was evaluated; all four were free `evaluation.check` runs (instance_count 2, solution_limit 2, execution_timeout 180). Each one hit `execution_timeout` on the example (n=27, m=5) without a solution.

- attempt-001: `Ints` with bounds 0..n+2, count equalities with `If(s[j]==i,1,0)`, default logic. Timeout.
- attempt-002: same encoding under `SolverFor("QF_LIA")`. Timeout.
- attempt-003: Boolean indicators `at[j][v] == (s[j]==v)` with one-hot rows, QF_LIA. Timeout.
- attempt-004: domains tightened to 0..n+1 for counts, QF_LIA, `If`-count encoding. Timeout.

Not tried: a reference-free search heuristic or a different decomposition of the counts. The check does not show whether any encoding finishes within 180 s, only that these four did not.
