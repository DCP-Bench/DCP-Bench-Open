Given a collection of integers, find a number of elements that sum to zero. -> one Boolean per element, indices[i] = 1 if nums[i] is selected (the output is the list of Booleans)
Find a number of elements (the instance gives m, the number to select) -> linear(*this, sel, IRT_EQ, m) (how many are true)
Elements that sum to zero -> linear(*this, IntArgs(nums), sel, IRT_EQ, 0) (weighted count: sum of nums[i] * sel[i] = 0)
Branching: decision variables are the selection Booleans -> branch(*this, sel, BOOL_VAR_NONE(), BOOL_VAL_MIN()); no objective (satisfaction)
