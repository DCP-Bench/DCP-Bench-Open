Select 8 of the 15 words so that the crossword can be completed.
  Each of the 8 entries (1 across, 2 down, 3 down, 4 across, 5 down, 6 down, 7 across, 8 across) takes one word of its length -> IntVar per entry with domain = words of that length, element table per position: element(IntArgs(letter of word k at position p), w_entry, cell) [i-th value of a table]
  Crossing cells agree -> the shared cell variable is the same variable in both entries' element posts (no extra constraint)
  Each word is selected at most once (8 different words) -> distinct(*this, w, IPL_DOM)
  Output E: word index for entries 1..8 in clue order -> output("E", w)
  Branching: entry words first (INT_VAR_SIZE_MIN, INT_VAL_MIN), then the cell letters so every variable is fixed
  Objective: none (satisfaction)
