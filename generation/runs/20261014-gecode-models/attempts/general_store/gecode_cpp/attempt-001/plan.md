# general_store plan (attempt-001)

Letters: C H E S A B O W P L, each a digit 0..9 (IntVarArray, one per letter).
Leading letters of the words (C, H, B, A, P, S) are not restricted to nonzero: the description does not say so.

- each different letter stands for a different digit -> distinct(*this, letters, IPL_DOM)
- the words above the line add to ALL WOOL -> linear(*this, coef, letters, IRT_EQ, 0, IPL_DOM), coef[letter] = sum of place values in the addends minus those in ALL WOOL
- branching: all letters INT_VAR_SIZE_MIN, INT_VAL_MIN (satisfaction, no objective)
- outputs: one int output per letter (A B C E H L O P S W)
