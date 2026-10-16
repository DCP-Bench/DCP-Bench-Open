Tommy was given 15 coins (half-crowns, shillings and sixpence) -> h + s + k == 15, one-hot count per coin type (0..15), integer sums
he found that he had 1 pound 5 shillings and 6 pence (306 pence) -> 30*h + 12*s + 6*k == 306 over the one-hot integer sums
each kind of coin is given (at least one of each) -> h >= 1, s >= 1, k >= 1 (makes the answer unique)
How many half-crowns was he given? -> output half_crowns = sum(v * h_v[v]); objective: satisfaction
