"cover all tasks" / "covers each piece of work exactly once" -> for each work w, sum of x_j over shifts j containing w = 1 (m.sum(..., "=", 1))
"select a subset of shifts" -> x_j boolean per shift, one per entry of the shifts list
"minimizing the total number of shifts used" / "cost of each shift is equal" -> minimize sum of x_j (m.sum)
"Print a binary list indicating which shifts were selected (x)" -> out x as BoolVar[num_shifts]
Objective: minimize the number of selected shifts (sum x_j).
