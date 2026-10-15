Binary sequence of length n, each bit S_i in {+1,-1} -> s_i Bool (true = +1), output 2*s_i - 1.
Periodic autocorrelation C_k = sum_i S_i * S_((i+k) mod n) -> d_{k,i} Bool = (s_i differs from s_((i+k) mod n)), so C_k = n - 2 * sum_i d_{k,i}.
Count of differing pairs v for lag k -> one-hot e_{k,v} over v in 0..n; sum(e_{k,.}) == 1 and sum_i d_{k,i} == sum_v v * e_{k,v} (PB).
Energy E = sum_{k=1}^{n-1} C_k^2 -> objective sum_k sum_v (n-2v)^2 * e_{k,v} (small weights, at most n^2).
Objective: minimize E.
