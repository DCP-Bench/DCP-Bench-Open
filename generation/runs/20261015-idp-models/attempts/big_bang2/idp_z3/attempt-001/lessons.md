Pairwise counts were written as a per-face helper cnt(i, j, a) = #{ b in Face: dice(i, a) > dice(j, b) } summed over a; accepted first try, not tested against the two-variable #{ a, b in Face: ... } form.
A product-free beats test: 'strictly more than half of 36 pairs' is beat_pairs >= 19, and the ten listed pairs cover all ten unordered die pairs, so the reverse direction follows.
