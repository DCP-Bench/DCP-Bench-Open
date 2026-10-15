# Plan: autoref (Paramita, one-hot entries)

Problem: S = (s_0 .. s_{n+1}) is a series of n+2 entries; for each i in 0..n, s_i is the number of occurrences of i in S; s_{n+1} = m.
Encoding: each entry s_k is a one-hot Bool block x[k][v] over values v in 0..n (an entry above n is uncounted; the reference rejects it); s_k = sum v * x[k][v].

- each entry s_k takes exactly one value -> one-hot `sum(x[k][v] for v) == 1`, value `s_k = sum(v * x[k][v])`.
- "there are s_i occurrences of i in S for each integer i from 0 to n" -> for i in 0..n: `sum(x[k][i] for k) == s_i` (count of value i over all entries equals the entry s_i).
- "s_{n+1} = m" -> `s_{n+1} == m`.
- objective: none (satisfaction); outputs: s = [s_0 .. s_{n+1}] as integer expressions.
