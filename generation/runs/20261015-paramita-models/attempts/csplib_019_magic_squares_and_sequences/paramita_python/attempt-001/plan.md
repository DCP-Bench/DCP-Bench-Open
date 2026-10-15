Plan: csplib_019_magic_squares_and_sequences (magic sequence of length n: value i occurs exactly x_i times)

- each x_i takes a value between 0 and n-1 -> one-hot xv[i][w] for w in 0..n-1, exactly one per position -> one-hot encoding.
- the number i occurs exactly x_i times -> per value i: sum over positions j of xv[j][i] == x_i, where x_i = sum(w * xv[i][w]) -> linear PB over one-hot Bools.
- output x = sum(w * xv[i][w]) per position.
- objective: none (satisfaction).
