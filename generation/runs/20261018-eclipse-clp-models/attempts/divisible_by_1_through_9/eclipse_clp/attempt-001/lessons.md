# Lessons, attempt-001 (divisible_by_1_through_9, eclipse_clp)

Not evaluated: every run below used `evaluation.check` (no attempt spent). Modelling stopped on context budget, not on rejection.

- Formulation: 10 digits in `ic`, `alldifferent`, leading digit nonzero, prefix values `P_n = 10*P_{n-1} + D_n`, quotient `Q_n` with `P_n #= n*Q_n`.
- Every variant timed out on the single instance (`execution_timeout`, "budget ran out during search"), 180 s budget:
  - `Q_n` labelled after all digits (default `labeling`, `first_fail` on everything): timeout. Quotients with 10^10 ranges are only fixed late, so failures come after the digits are chosen.
  - `Q_n` interleaved with `D_n` in the labelling list, `labeling/1` (left to right): about 120 s to the first solution in a direct run; check still timed out, since it must exhaust the tree after the first solution to get `complete`.
  - Same, with `search/6` `first_fail`: about 83 s to the first solution; still too slow for the second solution check.
  - Pairwise `#\=` instead of `alldifferent`: about 119 s to the first solution. No gain.
  - `P mod N #= 0` in place of the quotient: `instantiation fault in mod(_, 1, _)` from `ic` (the `mod` form did not compile as written in this integration).
- Estimate: roughly 10^4 search nodes, about 10 ms each in `ic`. The gap to a passing run is node count or per-node cost, not a missing constant.
- Next attempt should try a stronger formulation (for example `gfd` with split prefixes, since `gfd` is 32-bit, or redundant but description-derived constraints), not a larger budget.
