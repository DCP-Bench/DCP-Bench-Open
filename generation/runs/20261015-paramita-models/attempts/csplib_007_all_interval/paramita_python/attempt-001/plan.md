The twelve standard pitch-classes (c, c#, d, ...), represented by 0..11, each occur exactly once -> one-hot x[i][v] per position i, exactly one value per position, exactly one position per value (permutation)
the musical intervals between neighbouring notes cover the full set from 1 to 11 -> one-hot d[k][t] (t in 1..n-1) per neighbour pair k, exactly one interval per pair, each interval t used by exactly one pair (all-different)
for each neighbour pair, the interval equals the distance between the two pitch-classes -> If(x[k][a] & x[k+1][b], d[k][|a-b|]) for a != b
objective -> none (satisfaction); outputs x = sum(v * x[i][v]), diffs = sum(t * d[k][t])
