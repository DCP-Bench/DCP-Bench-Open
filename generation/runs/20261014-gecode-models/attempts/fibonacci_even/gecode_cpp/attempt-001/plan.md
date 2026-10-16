Each new term is the sum of the previous two terms, starting with 1 and 2 -> term[0] == 1, term[1] == 2, term[k] == term[k-1] + term[k-2] (linear, default propagation; the terms are fixed by these equalities)
Each term is one of the sequence terms; the first 40 terms are modelled (the 33rd term already exceeds four million, so later terms are excluded by their own bound) -> IntVarArray of 40 terms, domain 1..200000000 (covers term 40 = 165580141)
Print the sum of all the even-valued terms in the sequence which do not exceed four million (res) -> per term: small = (term <= 4000000), even = (term % 2 == 0), take = small && even, part = term * take; res = sum(part) (MiniModel expr, IPL default)
Branching: all decisions are fixed by the recurrence, so branch on the terms in order (INT_VAR_NONE, INT_VAL_MIN) so the space is fully assigned
Objective: none (satisfaction); output res only
