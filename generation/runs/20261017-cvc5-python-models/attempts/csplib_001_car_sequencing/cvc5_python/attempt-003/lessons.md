# csplib_001_car_sequencing, cvc5_python, attempt-003

Formulation: QF_LIA; one-hot Booleans x[p][c] with exactly-one; demand as Int sum of If(x,1,0); need[p][o] as the Or of the types requiring o; each station window as one clause per (at_most+1)-subset of its per_slots positions, all over Boolean need literals.

Result: accepted on example, json:1, json:3, json:6, json:7, json:9, json:10, json:12, json:13, json:15, json:16, json:17, json:19, json:20, json:21 (15/22 = 0.68, below the 0.8 retain threshold). Timeouts (180 s) on json:2, json:4, json:5, json:8, json:11, json:14, json:18.

Not retained: 15/22 < 0.8.

Next steps for a later attempt: the unsat-free search is slow on the harder instances. Untested ideas from the hints: implied bound on the first n - j*w positions (not seen but valid), and a Boolean totalizer for demand in place of the Int sum. Re-check the timed-out instances with the free check before a full evaluation.
