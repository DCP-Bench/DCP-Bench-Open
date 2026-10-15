Each shift is selected or not -> one Bool per shift, x[s] (output x, 0/1 per shift).
Select shifts that cover each piece of work exactly once -> for each work w: sum of x[s] over shifts s containing w == 1.
Minimise the total number of shifts used (every shift costs the same) -> objective: minimize sum of x[s].
