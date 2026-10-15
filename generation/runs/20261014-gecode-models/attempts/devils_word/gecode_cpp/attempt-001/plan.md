# Plan: devils_word

Requirement lines in the description's words.

- insert '+' or '-' before each integer in the array -> one IntVar per element, domain {-a_i, a_i} (IntSet of the two signed values), so each signed value is the output. `IntVarArray result(*this, n, ...)` with `IntSet` per element.
- summing them up will result in 666 -> `linear(*this, result, IRT_EQ, total)` (bounds propagation; subset-sum style, no decomposition).
- print the array with the correct signs (result) -> `output("result", result)`.
- branching -> `branch(*this, result, INT_VAR_SIZE_MIN(), INT_VAL_MIN())` over the signed values.
- objective -> none (satisfaction).
