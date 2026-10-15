sorted list of N elements -> a = instance["a"], N = len(a), K = instance["k"]
divide them into K groups by choosing K-1 split points -> split j is a position p_j in 1..N-1, binary bits split_j_bit_k (wide range, N up to 1000)
items with same value must be in the same group -> no split at position i where a[i-1] == a[i]: clause "p_j != i" per such i (bits differ from i)
split points ordered and groups non-empty -> p_j - p_{j-1} >= 1 (PB over binary weights); 1 <= p_j <= N-1
1-based split points, first group = elements 1..p_1 -> output x_j = p_j as integer expression sum(2^k * bit)
group size s_j = p_j - p_{j-1} (p_0 = 0, p_K = N) -> PB linear form with weights +-2^k
closest in size to round(N/K) -> t = round(N/K); error e_j in binary (bits err_j_bit_q), s_j - t <= e_j and t - s_j <= e_j as PB constraints
bound on e_j: sizes lie in [1, N-K+1], so |s_j - t| <= max(t-1, N-K+1-t); e_j needs bit_length of that bound
total error = sum of e_j -> objective minimize sum e_j (weights up to 2^(E-1), small)
