# Plan: csplib_084 Hadamard matrix Legendre pairs
- sequences A = a_1..a_l, B = b_1..b_l with entries in {-1,+1}, odd l, m = (l-1)/2 -> one Bool per entry, true means +1
- a_i * a_{i+s} = +1 exactly when the two signs agree -> per shift s and position i one Bool agreement indicator, Iff(agree, Iff(a_i, a_j)) with j = (i+s) mod l
- c_s: PAF(A,s) + PAF(B,s) = -2 (s = 1..m) -> PAF(A,s) = 2*E_A(s) - l, so E_A(s) + E_B(s) = l - 1 (sum of agreement indicators == l-1)
- c_{m+1}: a_1 + ... + a_l = 1 -> number of +1 entries == (l+1)/2 (PB over the Bools)
- c_{m+2}: b_1 + ... + b_l = 1 -> number of +1 entries in B == (l+1)/2
- outputs a, b -> 2 * bit - 1 per entry (values -1 or +1)
- objective: none (satisfaction)
