# Plan: five_statements (attempt-001)

Five Boolean statements s[0..4]; statement i (1-based) says "exactly i of these statements are false".
Let t = number of true statements, so the number of false statements is 5 - t.

- "statement i is true iff exactly i statements are false" -> s[i-1] == (expr(sum(s) == 5 - i)); with sum(s) = t, that is t == 5 - i. Posted as a reified equivalence per statement via expr(*this, total == 5 - i) and rel(s[i-1] == eq) (no global fits; the statement is a reified equality on a sum, which is the map row "how many are true" for linear with IRT_EQ, reified).
- "how many statements are true" -> total = expr(*this, sum(s)) (linear sum, bounds propagation).
- Branching: the five Booleans decide everything (total is fixed by them); branch on s with BOOL_VAR_NONE() and BOOL_VAL_MIN().
- No objective: satisfaction. Output statements = s (BoolVarArray, shape [5]).
