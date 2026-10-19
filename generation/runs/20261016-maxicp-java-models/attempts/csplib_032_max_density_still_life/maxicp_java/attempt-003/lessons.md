# csplib_032 max density still life, maxicp_java: lessons (retry)

Outcome: not retained. Attempt 003 is accepted on the example (6x6, optimum 18) and json:1 (7x7), and times out on json:2 (8x8, optimum 36) at the 180 s limit. It checked 2 of 3 available instances (67%), below the 80% threshold. This is a performance limit.

Encoding in attempt 003: one Boolean per cell (registered, row-major), and for each padded board position a neighbour count `sum(...)` over the in-grid neighbours, with `table((centre, count))` for the rules (live: count 2 or 3; dead: count not 3). Attempts 001 and 002 used reified sums and a 9-ary table per cell. All three are accepted on the small instances and time out on json:2.

Evidence that the cost is the optimality proof: the reported first solution on json:2 already has 36 live cells (the optimum), so the search finds the optimum fast and then cannot close the bound. The timeout is the same for all three encodings, so the choice of local constraint did not change it.

Not tried, and not claimed to help: redundant local density bounds (any bound must be derived from the rules; a bound taken from the known optimum is forbidden), and a different objective encoding. A 2x2 block with exactly three live cells does not give a direct constraint: its missing cell can still reach a count other than 3 through outside neighbours.
