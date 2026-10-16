# packing_rectangles / maxicp_java, attempt 001

Accepted and retained. Pairwise disjunctive non-overlap (four reified `isLe` per pair, posted with `or`),
totals bounded below by `sumArea / other side`, area as a plain objective variable with `eq(area, mul(totalX, totalY))`.

Performance limit: `json:1` (eight squares of side 1..8, optimum 210) times out at 180 s with
"Candidate optimum was not proven". The other four instances are accepted (example, json:2 at about 100 s, json:3, json:4).
The brief's `[4]int` shapes come from the example only; arrays are sized from each instance's `widths`.
