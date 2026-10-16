# Plan: autoreferential series S = (s0, ..., sn, sn+1) (autoref)

- "non-empty finite series S = (s0, s1, ..., sn, sn+1)" -> n+2 terms: s = intVarArray(n+2)
- "every value in S is counted, since the occurrences are counted for i from 0 to n": each s_k in 0..n (a value above n would not be counted)
- "there are si occurrences of i in S for each integer i from 0 to n" -> for each i in 0..n: m.count(i, s, s[i])
- "sn+1 = m" -> s[n+1] = m (arithm); m must be <= n to be a counted value
- objective: satisfaction (none)
- instance fields: n, m (both read from the instance)
