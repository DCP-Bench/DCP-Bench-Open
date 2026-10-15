# Plan: big_bang2 (nontransitive dice), attempt 001 (order encoding)

Problem: five dice (Rock, Paper, Scissors, Lizard, Spock), six faces each, face values 1..12, repeats allowed.
Die A beats die B when A has a strictly larger face than B in more than half of the 36 face pairs (more than 18).
Ten beats relations (winner, loser), 0-indexed: Rock>Scissors, Rock>Lizard, Paper>Rock, Paper>Spock, Scissors>Paper, Scissors>Lizard, Lizard>Paper, Lizard>Spock, Spock>Rock, Spock>Scissors.

- each face value in 1..12 -> order (unary) Bools ge_d_k_t = "face >= t" for t = 2..12; monotone (ge t+1 -> ge t); value = 1 + sum(ge)
- "face a > face b" -> OR over t of (ge_a_t & ~ge_b_t)  (a >= t and b < t)
- for each beats pair (A, B) and face pair (i, j): gt -> (A_i > B_j); sum(gt over 36 pairs) >= 19
  (only the implication is needed: gt is true only when the comparison holds, and the count forces enough true)
- output dice = the 5x6 face value expressions
- objective: none (satisfaction)
