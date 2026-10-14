# Plan: frog_circle (attempt-001)

Problem: cards 1..n on a circle, x[i] = card at position i (0-based, clockwise). The frog starts on card 1 and jumps k places clockwise from card k. Find an arrangement where the frog lands on every card.

- the cards are a permutation of 1..n -> distinct(*this, x, IPL_DOM)
- rotating the arrangement gives the same circle: card 1 sits at position 0 -> rel(*this, x[0] == 1); the frog starts at position 0
- jump map: from position i the frog lands on (i + x[i]) mod n -> succ[i] == (i + x[i]) % n
- the frog's visits: p[0] = 0 (its start), p[j+1] = succ[p[j]] for j < n-1 -> element(*this, succ, p[j], p[j+1])
- it visits every card once in its first n jumps -> distinct(*this, p, IPL_DOM) (the visited positions are all of 0..n-1; cards then cover 1..n)
- note: the frog may get stuck after the last card (a rho shape, not a cycle); n=4 gives only (1,2,4,3), which is such a case, so no circuit
- branching: cards in position order, smallest first; then succ; then the visit order p (in order, smallest value first)
- objective: none (satisfaction)
