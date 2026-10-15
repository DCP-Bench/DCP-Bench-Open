Schedule 4 people into 4 interview slots -> n = m.size(); one slot IntVar per person, domain = the slots where that person is free (m[i][j] = 1).
each person is free only in their free slots (m[i][j] = 1) -> IntVar slot_i(*this, IntSet(free slots of i)) and channel(*this, x_i row, slot_i) (one-hot x[i][j] = 1 iff slot_i = j, so x[i][j] = 0 wherever m[i][j] = 0).
each person is assigned exactly one slot -> channel one-hot row (x_i has a single 1 by channel).
each slot has at most one person (interview slots are not shared) -> distinct(*this, slot, IPL_DOM).
each slot has exactly one person (4 people, 4 slots) -> linear(*this, column j of x, IRT_EQ, 1), redundant with distinct, kept for the Boolean view.
branching -> branch on slot_i with INT_VAR_SIZE_MIN, INT_VAL_MIN (determines every x).
objective -> none (satisfaction).
