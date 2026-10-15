# Plan: handshaking (attempt 001)

Hilary and Jocelyn are married; they invite num_couples couples (persons 2k, 2k+1; couple 0 = Hilary and Jocelyn).
-> persons 0..2n+1, spouse of p is p XOR 1; couple 0 is persons 0 (Hilary) and 1 (Jocelyn).

Nobody shakes hands with him or herself or with his or her spouse.
-> Bool shake_i_j only for i < j, not spouses; no variable for self or spouse pairs.

Everyone except Jocelyn is asked how many hands they shook; all answers are different.
-> deg(p) = sum of shake bools at p; one-hot oh[p][v] over v in 0..2n with sum == 1 and deg(p) == sum v*oh[p][v];
   per value v: sum over p != Jocelyn of oh[p][v] == 1 (all answers distinct, 2n+1 people, 2n+1 values).

Print the number of hands Hilary has shaken (hil).
-> output hil = deg(Hilary).

Objective: satisfaction, no objective.
