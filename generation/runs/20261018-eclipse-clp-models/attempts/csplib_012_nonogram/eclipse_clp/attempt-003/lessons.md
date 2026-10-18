# Lessons, csplib_012_nonogram, eclipse_clp

Attempt 1 (retained) is accepted on 11 of 13 instances. json:2 (p200, 25x25) and json:6
(castle, 35x60) hit execution_timeout at 180 s in all three attempts. 11/13 = 0.85 is
above the 0.8 floor, so attempt 1 is kept as a performance limit.

- Attempt 1: start variables per block, reified `In #= (S #=< J and S + B #> J)` per
  square and block, `default labeling`. Fastest of the three (merka 35 s).
- Attempt 2: same encoding, `search/6` with `first_fail`. Same two timeouts, slightly slower.
- Attempt 3: explicit leftmost/rightmost start domains and the redundant
  `sum(Cells) #= sum(Blocks)`. Same two timeouts, slower overall (merka 89 s).

Not tried: a table or DFA encoding per line (`gfd` `table/2` or `regular/2`), which
propagates more than the reified start encoding. That is the next formulation to try for
the two timeouts.
