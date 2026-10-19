# session1_magic_square on cvc5_python: lessons

Evaluated attempts: 001 and 002. Both accepted on the example, json:1 (n=1) and json:2 (n=3), and both hit `execution_timeout` (180 s) on json:3 (n=5) and json:4 (n=6). That is 3/5 instances checked, below the 0.8 retain threshold, so nothing is retained.

- 001: integer cells, `Distinct` over 16 cells, row/column/diagonal sums as linear equalities. Accepted on n=1, 3, 4; timeouts on n=5, 6.
- 002: one Boolean per (cell, value) with pairwise exactly-one constraints, cell value as an integer equal to a sum of `If` terms. Same pattern: n=1, 3, 4 accepted, n=5, 6 timeout. The n=4 example took about 18 s here against about 5 s in 001.
- 003 (not evaluated, checked free on json:3 only): the same Boolean one-hot encoding with line sums written directly over the `If` terms, then a 0/1 integer version with linear sums. Both time out on n=5 (the 0/1 version exceeded the 190 s container limit).

Reading: every encoding tried, Int with `Distinct` and one-hot Boolean with `If` or with 0/1 Int, is correct and fast for n <= 4 but cvc5 does not find a magic square of order 5 within 180 s. The remaining levers in the solver skill (`QF_LIA` and similar logic settings, `tlimit-per`) are not applied by the runner, so they cannot help here. Not tried: a different search order (the runner does not expose one), and a larger time limit (not in the frozen profile).

No reference file was read. No skill or contract gaps were found in this problem.
