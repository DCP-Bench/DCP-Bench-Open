# Plan: handshaking (attempt 002)

Changed from attempt 001: the hand counts use a unary (order) encoding instead of one-hot,
because attempt 001 timed out on the 8-couple example while enumerating a second answer.

Hilary and Jocelyn are married; they invite num_couples couples who are friends (persons 2k, 2k+1; couple 0 = Hilary and Jocelyn).
-> persons 0..2n+1, spouse of p is p XOR 1; Hilary is person 0, Jocelyn is person 1.

Nobody shakes hands with him or herself or with his or her spouse.
-> Bool shake_i_j only for i < j, not spouses; no variable for self or spouse pairs.

Everyone except Jocelyn is asked how many hands they shook; all answers are different.
-> ge[p][k] <=> (hands of p >= k), for k = 1..2n, unary Iff with a PB comparison, and If(ge[k+1], ge[k]).
   All answers different: sum over asked p of ge[p][k] == 2n+1-k for each k (2n+1 people, values 0..2n each used once).

Print the number of hands Hilary has shaken (hil).
-> output hil = hands(Hilary) as an integer expression.

Objective: satisfaction, no objective.
