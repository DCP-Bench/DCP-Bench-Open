Problem: n people on a waiting list; compatible[i] = people i can donate a kidney to (directed). Choose transplants t[i][j] = 1 if i donates to j. Maximise the number of people receiving a kidney. Anyone who gives must receive; nobody receives more than one.

- "compatible[i] is the set of people to which i can donate" -> t[i][j] = 0 for j not in compatible[i] (and for i = j) -> m.arithm(t[i][j], "=", 0)
- "no person receives more than one kidney" -> received_j = sum_i t[i][j], domain 0..1 -> m.sum(column_j, "=", received_j)
- "anyone who gives a kidney must receive one" -> given_i = sum_j t[i][j], domain 0..1; given_i <= received_i -> m.sum(row_i, "=", given_i), m.arithm(given_i, "<=", received_i)
- "maximize the number of people that receive a new kidney" -> total = sum_j received_j -> m.sum(received, "=", total), setObjective MAXIMIZE total
- search (repair for attempt-001 execution_timeout on the 20-person dense instance): domOverWDeg over all transplant cells, Luby restarts (50 fails)
