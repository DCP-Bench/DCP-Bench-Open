# plan: csplib_007_all_interval (attempt-002, repair of attempt-001 timeout on n=20)

Given n, find s, a permutation of 0..n-1 (the pitch classes)
-> x[0..n-1] in 0..n-1, m.allDifferent(x, "AC")
the interval vector v = (|s_2 - s_1|, ..., |s_n - s_{n-1}|) is a permutation of 1..n-1
-> diffs[0..n-2] in 1..n-1 with dx_i = x[i+1] - x[i], diffs_i = |dx_i| (m.absolute), m.allDifferent(diffs, "AC")
search: dom/wdeg on x and diffs with Luby restarts (attempt-001 timed out on n=20 with the default search)
objective: none (satisfaction); outputs x (n integers) and diffs (n-1 integers)
