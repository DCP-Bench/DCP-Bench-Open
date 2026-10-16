# Plan: arch_friends (attempt-001)

Stops are visits 1..4. Shoe outputs give each shoe's visit, store outputs give each store's visit.

- each shoe bought at a different stop (the four shoes occupy the four visits) -> distinct(*this, shoes, IPL_DOM)
- each store is a different stop (the four stores occupy the four visits) -> distinct(*this, stores, IPL_DOM)
- Harriet bought fuchsia flats at Heels in a Handcart (same stop) -> rel(*this, heelsinahandcart == fuchsiaflats) (equal variables, one stop)
- the store visited just after purple pumps was not Tootsies: tootsies != purplepumps + 1 -> rel(*this, tootsies != purple + 1) (minimodel expression, no decomposition) (vacuous when purple pumps is the last stop)
- The Foot Farm was the second stop -> rel(*this, footfarm == 2)
- two stops after The Shoe Palace, suede sandals: suedesandals == theshoepalace + 2 -> rel(*this, suede == palace + 2) (minimodel expression)
- branching: branch on the shoe visits, then the store visits, INT_VAR_SIZE_MIN, INT_VAL_MIN
- objective: none (satisfaction)
