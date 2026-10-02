Native `addMultiplication(["a", "b"], ...)` plus `addMultiplication(["n", "n"], ...)` (attempt-001)
timed out on 3 of 5 instances (max_val 10000, 1200 and 1700), twice with no runner status
("Process exceeded 190 seconds"), so `toOptimum(timeout)` did not return near its budget.
Replacing the product by a table of the triples (a, b, n) with a*b == n*n, listed from the
square-free parts of the numbers, and channelling the chosen triple to the difference p
(attempt-002 without the channel, attempt-003 with it) solved all five instances in 33 s in
total. Evidence: attempt-001/evaluation.json, attempt-002/evaluation.json, attempt-003/evaluation.json.
