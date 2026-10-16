Problem: binary sequence of length n, bits in {-1,+1}; periodic autocorrelations C_k = sum_i S_i*S_{(i+k) mod n}; minimise E = sum_{k=1}^{n-1} C_k^2. Output sequence as the list of ±1 values.
- each bit is +1 or -1 -> S[i] IntVar with domain {-1,1}
- each product S_i * S_{(i+k) mod n} -> m.times(S_i, S_j, P[k][i])
- C_k is the sum of the n products for shift k -> m.sum(P[k], "=", C[k])
- C_k^2 -> m.square(Q[k], C[k])
- E = sum of the Q_k over k = 1..n-1 -> m.sum(Q, "=", E); objective MINIMIZE E
- sequence output = S
