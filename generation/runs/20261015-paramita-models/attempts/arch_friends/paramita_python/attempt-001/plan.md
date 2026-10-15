# Plan: arch_friends (4 shoes, 4 stores, stops 1..4)

- Harriet bought four shoe pairs at four stops, each stop one shoe and one store -> one-hot Bools per item over stops 1..4: sh[item][p].
- Each shoe is bought at exactly one stop, each stop has exactly one shoe -> per item: sum_p sh == 1; per stop: sum over the four shoes == 1.
- Each store is visited at exactly one stop, each stop has exactly one store -> same pattern for stores.
- Clue 1: fuchsia flats were bought at Heels in a Handcart -> fuchsiaflats == heelsinahandcart (integer PB equality).
- Clue 2: store visited just after purple pumps was not Tootsies -> for stop k in 1..3: ~(purplepumps at k & tootsies at k+1).
- Clue 3: Foot Farm was the second stop -> footfarm at stop 2 (single literal).
- Clue 4: two stops after The Shoe Palace, suede sandals -> theshoepalace + 2 == suedesandals (integer PB).
- Outputs: each item's integer stop value = sum(p * sh[item][p]).
- Objective: none, satisfaction problem.
