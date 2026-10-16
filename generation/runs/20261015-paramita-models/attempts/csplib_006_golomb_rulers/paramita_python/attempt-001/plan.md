m marks 0 = a_1 < a_2 < ... < a_m -> position Bool b_p for p in 0..L (true = a mark at p); b_0 true; sum(b) == m.
Domain bound L = length of the Erdos-Turan ruler 2*p*k + (k*k mod p), k = 0..m-1, p the smallest prime >= m (derived construction, not the instance table).
all m(m-1)/2 differences distinct -> for each difference d in 1..L, q_{p,d} with (b_p and b_(p+d)) -> q_{p,d}; sum_p q_{p,d} <= 1 (PB).
k-th mark position a_k -> unary count G_{p,k} = "at least k marks in positions 0..p" (recurrence G_{p,k} <-> G_{p-1,k} or (b_p and G_{p-1,k-1})); a_k = (L+1) - sum_p G_{p,k} (PB).
length a_m -> objective: minimise a_m.
