# coins_grid, maxicp_java: lessons from attempts 001 and 002

Attempt 001 (retained by mistake, does not count): row and column sums plus
`mul(x, i*j)` views with `maximize(sum i*j)`. Timed out (proof not reached) on
the 10x10, 7x7 and 12x12 instances. Its objective direction did not match the
brief (minimise z).

Attempt 002 (retained): minimise z directly. Per row and per column, a `table`
over all c-subsets of the line, extended with the line's cost (sum of
(i-j)^2 over its coins), and each line cost is an unregistered `makeIntVar`
with the min/max over the patterns as bounds. z is an unregistered variable
equal to the sum of the row costs and to the sum of the column costs, with
domain max/min of the two bound sums. Result: the 10x10, 7x7, 8x8 and 6x6
instances prove optimality in 2 to 14 s.

Performance limit: the 12x12, c=5 instance (optimum 234) does not prove
optimality within 180 s, nor within 600 s when checked with a longer limit.
The evaluation covers 4 of 5 instances (80%). The search is plain DFS with
no learning; the table over 792 patterns per line gives row-wise bounds only,
and the column costs do not tighten the row bounds beyond domain filtering.
Not tried: a per-line choice variable with element views, or a stronger
bound over the remaining free cells.
