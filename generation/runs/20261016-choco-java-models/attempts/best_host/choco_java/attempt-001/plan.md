Six guests (0 Andrew, 1 Betty, 2 Cara, 3 Dave, 4 Erica, 5 Frank) seated around a round table, each seat holds one guest -> x is a permutation of 0..5: allDifferent(x, "AC")
Andrew will only sit next to Dave and Frank -> table on the seat pair (x[i], x[i+1 mod 6]) with the allowed pairs of Andrew (0-3, 0-5)
Betty will only sit next to Cara and Erica -> allowed pairs 1-2, 1-4
Cara will only sit next to Betty and Frank -> allowed pairs 2-1, 2-5
Dave will only sit next to Andrew and Erica -> allowed pairs 3-0, 3-4
Erica will only sit next to Betty and Dave -> allowed pairs 4-1, 4-3
Frank will only sit next to Andrew and Cara -> allowed pairs 5-0, 5-2
Minimise conflicts: a zero-conflict seating exists (cycle A-D-E-B-C-F-A), so the neighbour rules are posted as hard table constraints, and every solution has zero conflicts (the brief declares satisfaction)
Objective: none (satisfaction); output x
