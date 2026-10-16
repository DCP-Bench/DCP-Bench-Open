# cabling plan (attempt-001)
Rack of n 1U slots; each device sits in one slot, one device per slot (permutation).
- device d in slot k: one-hot p[d][k], exactly one slot per device (sum == 1), each slot holds exactly one device (sum == 1)
- cable length between two devices = distance between their slots: one-hot d_ab[j] for j in 0..n-1, exactly one value; per slot pair (k,l): p[a][k] & p[b][l] -> d_ab[|k-l|]
- sum of all cable lengths: minimise sum over cable entries of count * j * d_ab[j]; this objective is final_sum
