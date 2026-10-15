# Plan: csplib_033 word design

- num_words words of length n, letters A=0, C=1, G=2, T=3 -> one-hot Bools x[w][p][l], exactly one letter per position
- output words: value = sum((l+1) * x[w][p][l]) -> ints 1..4
- each word has exactly 4 symbols from {C,G} -> sum over p of (x[w][p][C] + x[w][p][G]) == 4
- distinct words differ in at least 4 positions -> diff Bool d per pair and position, d -> letters differ, sum(d) >= 4 for each pair w1 < w2
- x^R and y^C differ in at least 4 positions for every ordered pair (x, y), including x = y -> complement of letter l is 3 - l; d -> x[w1][n-1-p] != comp(x[w2][p]); sum(d) >= 4
- satisfaction problem, no objective
