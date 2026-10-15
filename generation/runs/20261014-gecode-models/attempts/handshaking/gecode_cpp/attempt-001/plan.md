Hilary and Jocelyn are married -> shake[pair(0,1)] = 0 (spouses, posted as bool == 0)
They invite a number of couples -> people = 2n+2: Jocelyn (0), Hilary (1), couples 2k+2, 2k+3 (k < n)
Nobody shakes hands with him or herself -> no self variables; handshakes are only pairs i < j
Nobody shakes hands with his or her spouse -> shake[pair(a,b)] = 0 for each couple (a,b) incl. Hilary-Jocelyn
The number of hands each person has shaken -> hands[i] = sum over j != i of shake[pair(i,j)] (linear, rel with sum)
All the answers are different (everyone but Jocelyn is asked) -> distinct(*this, hands[1..2n+1], IPL_DOM)
Hands range 0..2n (no self, no spouse) -> hands[i] in 0..2n domain
Branching -> branch(hands of asked people, INT_VAR_SIZE_MIN, INT_VAL_MIN), then branch(shake, BOOL_VAR_NONE, BOOL_VAL_MIN)
Output hil -> output("hil", hands[1]); satisfaction, no objective
