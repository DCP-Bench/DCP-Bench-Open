Each of the blocks has a single letter on each of its sides; the blocks contain every letter but Q and Z.
  -> dice[i] = block of letter i (one IntVarArray over the instance's alphabet, domain 0..num_blocks-1)
Each block has exactly num_sides letters.
  -> count(*this, dice, b, IRT_EQ, num_sides) for every block b
A word can be spelled by arranging the blocks, so the letters of a word must lie on distinct blocks (one letter per block at a time). The word's letters are each on a different block.
  -> distinct(*this, dice[word letters], IPL_DOM) for each word
Branching: dice in order with the smallest-domain variable first, smallest value first.
  -> branch(*this, dice, INT_VAR_SIZE_MIN(), INT_VAL_MIN())
Objective: none, satisfaction problem; output the dice assignment.
  -> output("dice", dice)
