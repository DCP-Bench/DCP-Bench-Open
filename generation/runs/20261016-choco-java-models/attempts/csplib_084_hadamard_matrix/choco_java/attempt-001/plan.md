# Plan: Hadamard matrix Legendre pairs (csplib_084)

Two sequences a[l], b[l] with values -1 or 1, l from the instance.

- a_i in {-1, +1}, b_i in {-1, +1} -> m.intVar("a", new int[]{-1, 1}) per entry
- for every shift s = 1..m (m = (l-1)/2): PAF(A,s) + PAF(B,s) = -2 -> per s, products a_i * a_{(i+s) mod l} and b_i * b_{(i+s) mod l} as IntVars in {-1,1} (m.times), then m.sum over all 2l products "=" -2
- c_{m+1}: a_1 + ... + a_l = 1 -> m.sum(a, "=", 1)
- c_{m+2}: b_1 + ... + b_l = 1 -> m.sum(b, "=", 1)
- Output a and b -> out.put("a", a), out.put("b", b)
- Objective: satisfaction, none
