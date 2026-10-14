# Plan: bowls and oranges (attempt-001)

Requirements in the description's words:
- "place all the oranges in the bowls, no more than one orange in each bowl" -> bowl x[i] of orange i, x strictly increasing (sorted output, one orange per bowl) -> rel(*this, x[i], IRT_LE, x[i+1]) (strict chain, implies distinct; no map row needed for a sorted strict chain)
- "one orange in each bowl" occupancy link -> o[k] = 1 iff some orange is in bowl k -> count(*this, x, k, IRT_EQ, o[k]) (o[k] an IntVar 0..1: count needs an IntVar cardinality, a BoolVar does not convert)
- "no three oranges A, B, C such that AB = BC" -> for each bowl b and gap d with a = b-d >= 1, c = b+d <= n: not all of o[a], o[b], o[c] -> linear(*this, {o[a], o[b], o[c]}, IRT_LQ, 2) (no global fits; a 3-term arithmetic progression on 0..1 flags, decomposition by necessity)
- Branching: the oranges' bowls in order, first-fail with AFC, min value first, Luby restarts (heavy-tailed satisfaction search per skill); then the occupancy Booleans.
- Objective: satisfaction (none).
- Bowls are numbered 1..n (the description places them at 1 m intervals from a start point; 1-based assumed).
