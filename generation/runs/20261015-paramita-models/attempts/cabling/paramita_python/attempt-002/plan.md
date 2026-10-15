# cabling plan (attempt-002): smaller encoding for the 10-device instance
Attempt-001 timed out on the 10-device instance (one-hot distance per cable with n^2 implications each).
- device d in slot k: one-hot place[d][k], exactly one slot per device, exactly one device per slot (permutation)
- slot of device d as an integer expression: pos_d = sum(k * place[d][k])
- cable length of entry [a, b, count] as an integer t in unary (t_ge[m] for m in 1..n-1, If(t_ge[m+1], t_ge[m]))
- length is at least the difference both ways: pos_a - pos_b <= t and pos_b - pos_a <= t; minimisation makes t equal |pos_a - pos_b|
- sum of all cable lengths: minimise sum(count * t) over cable entries; this is final_sum
