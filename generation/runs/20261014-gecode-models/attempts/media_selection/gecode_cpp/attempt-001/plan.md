Problem: choose advertising media so every audience is reached at least once, at minimum total cost.
- media j is selected or not -> one BoolVar per media, sel[j] (output is_selected)
- every audience must be reached by a selected medium (set covering) -> for audience i, linear over the media that reach it: sum(sel[j] : incidence[i][j] = 1) >= 1 -> linear(*this, cover, IRT_GQ, 1) with cover built per audience
- total cost of selected media -> total = sum(media_costs[j] * sel[j]) -> expr(*this, sum(IntArgs(costs), sel))
- minimise campaign cost -> minimize(total); output min_total_cost
- branching: selection booleans first, AFC variable choice with restarts, value 0 first (leave a medium out unless a cover needs it)
