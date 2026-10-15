take items with weights and values; total weight of the items in the backpack must not exceed the capacity -> linear(*this, weights, x, IRT_LQ, capacity)
which items to take as booleans x[i] (True = taken) -> BoolVarArray x(*this, n, 0, 1) as output x
maximize the total value of the items in the backpack -> total = IntVar via linear(*this, values, x, IRT_EQ, total); maximize(total)
branching: BOOL_VAR_NONE with BOOL_VAL_MAX (decisions are the x booleans; the objective IntVar is fixed by propagation)
