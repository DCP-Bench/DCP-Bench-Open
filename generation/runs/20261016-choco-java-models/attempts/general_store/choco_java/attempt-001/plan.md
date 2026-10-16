Problem: cryptarithm, each letter a different digit 0-9; the 16 addends sum to ALL WOOL.
- each letter a different digit -> 10 IntVars in 0..9 -> m.allDifferent(L, "AC")
- each addend, read as a number in base 10 -> m.scalar(L, place-value coefficients, "=", wordValue)
- ALL WOOL, read as a number -> m.scalar(L, coefficients, "=", total)
- the 16 addend values sum to ALL WOOL -> m.sum(wordValues, "=", total)
- no leading-zero rule in the description, so none is posted
Objective: none (satisfaction). Outputs: each letter as an int.
