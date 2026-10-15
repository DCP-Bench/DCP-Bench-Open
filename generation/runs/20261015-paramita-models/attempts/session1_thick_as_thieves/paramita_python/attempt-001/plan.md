# Plan: session1_thick_as_thieves (satisfaction, outputs artie..fingers as guilty bools)
Guilty status g_X is a Bool per suspect; a truth-teller is innocent, a liar is guilty, so statement true <=> innocent.
- "the getaway car was barely big enough to hold two, at least four innocent" -> sum(g) <= 2
- "the guilty one or ones" -> sum(g) >= 1
- Artie "It wasn't me." -> Iff(~gA, ~gA)
- Bill "Crackitt was in it up to his neck." -> Iff(~gB, gC)
- Crackitt "No I wasn't." -> Iff(~gC, ~gC)
- Dodgy "If Crackitt did it, Bill did it with him." -> Iff(~gD, Or(~gC, gB))
- Edgy "Nobody did it alone." (guilty set is not a singleton) -> Iff(~gE, Or(sum(g)==0, sum(g)>=2))
- Fingers "Artie and Dodgy together." (guilty set is exactly {A, D}) -> Iff(~gF, And(gA, gD, ~gB, ~gC, ~gE, ~gF)) with the F term dropped (F innocent required by set) ; written as exact set.
- Objective: none (satisfaction). Encoding: Bool per suspect, no integers.
