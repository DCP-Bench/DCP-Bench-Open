# knights_tour, highs_cpp, attempt 002

Accepted by the evaluator with 3 of 5 instances checked (ratio 0.6), so not retained.

- Time-indexed binaries on[s][k] (k of the square's colour, k >= knight distance from the corner),
  one-per-square and one-per-move rows, successor and predecessor rows, and an integer pos[s] tied by an equality row.
- Corner start (0,0) at move 0 and second square (1,2) by diagonal reflection, both fixed by bounds.
- Arc degree rows (next[s][t]) on top: no gain on the 8x8 board.
- 8x8 (json:1): the first solution alone took about 120 s with the corner start, but the second
  enumeration solve (solution_limit 2) runs past the 180 s limit. Without the corner start, not even the first solution came in 180 s.
- 10x10 (json:2): timeout, not tried further.
- 5x5, 7x7 and the 6x6 example pass (0.3 s, 29 s, 12.6 s).

Next idea if this is retried: a formulation that finds the first 8x8 tour in well under 60 s, since
the enumeration solve doubles the time. Not tried: a CP-style all-different plus successor structure
expressed with fewer binaries.
