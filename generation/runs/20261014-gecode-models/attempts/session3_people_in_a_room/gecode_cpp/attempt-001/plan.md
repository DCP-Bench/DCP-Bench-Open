# Plan: session3_people_in_a_room (gecode_cpp, attempt-001)

Model: seq[i] = 1 if the i-th person to enter is female, 0 if male (output order = entry order). 13 entries, no instance data.

- "There are 13 people" -> seq = BoolVarArray(13, 0, 1), no other variables.
- "4 of them are male" -> 9 females: `linear(*this, seq, IRT_EQ, 9)` [how many are true].
- "ratio of females to males in the room at any one time is no greater than 7/3" -> for each prefix of length k (the room after the k-th entry), F_k <= 7/3 * (k - F_k), i.e. F_k <= floor(7k/10): `linear(*this, prefix_k, IRT_LQ, 7*k/10)` [how many are true] for k = 1..13. An empty room (k = 0) is trivially fine. Prefix k = 1 forces the first entrant to be male.
- "Find a way that the males and females enter" -> satisfaction, no objective.
- Branching: entry order, `BOOL_VAR_NONE()`, `BOOL_VAL_MIN()` (male first, which keeps the prefix constraints easy).
