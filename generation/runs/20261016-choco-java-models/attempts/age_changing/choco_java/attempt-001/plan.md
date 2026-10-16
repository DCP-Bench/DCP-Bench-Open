# age_changing plan (attempt-001)

Ages: m (my age), h (husband's age), integers 0..B with B = 2000 (assumed generous bound; ages are not bounded in the statement).
Operations: 0 = +2, 1 = /8 (exact), 2 = -3, 3 = *7. Each sequence uses all four once.

- "start with my age ... apply the four operations in some order, final answer is husband's age" -> sequence A: 4 op slots, allDifferent over the op slots; value chain m -> ... -> h via table(op, in, out) per step
- "start with his age and apply the same four operations in a different order, you get my age" -> sequence B: 4 op slots, allDifferent; value chain h -> ... -> m via the same table
- "different order" -> the op vectors of A and B differ in at least one slot (m.or of slot-wise ne)
- "/8" -> only exact division: the table has an in/out pair only when in is a multiple of 8, and -3 only when in >= 3, so no negative ages
- Objective: none (satisfaction). Outputs: m, h.
