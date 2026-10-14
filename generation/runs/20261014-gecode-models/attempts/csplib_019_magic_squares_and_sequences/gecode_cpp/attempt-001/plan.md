the sequence has length n; x_i is between 0 and n-1 -> IntVarArray x(*this, n, 0, n-1)
for each i, the number i occurs exactly x_i times in the sequence -> count(*this, x, cards = x, IntArgs(0..n-1)) [gcc: value j occurs cards_j times, cards are the x themselves]
the counts add up to the length (implied, redundant) -> linear(*this, x, IRT_EQ, n)
branching: x in order, smallest domain first, smallest value first -> branch(*this, x, INT_VAR_SIZE_MIN(), INT_VAL_MIN())
objective: none, satisfaction; output x
