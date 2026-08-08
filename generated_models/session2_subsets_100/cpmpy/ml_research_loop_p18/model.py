import json

values = [81, 21, 79, 4, 29, 70, 28, 20, 14, 7]
n = len(values)
for s_mask in range(1, 1 << n):
    s_sum = sum(values[i] for i in range(n) if s_mask & (1 << i))
    remaining = [i for i in range(n) if not s_mask & (1 << i)]
    for t_submask in range(1, 1 << len(remaining)):
        t_mask = 0
        for pos, index in enumerate(remaining):
            if t_submask & (1 << pos):
                t_mask |= 1 << index
        if sum(values[i] for i in range(n) if t_mask & (1 << i)) == s_sum:
            in_s = [1 if s_mask & (1 << i) else 0 for i in range(n)]
            in_t = [1 if t_mask & (1 << i) else 0 for i in range(n)]
            print(json.dumps({"in_S": in_s, "in_T": in_t}))
            raise SystemExit
