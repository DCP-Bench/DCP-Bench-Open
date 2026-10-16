Allocating advertising budgets between possible advertising outlets -> is_selected[m] BoolVar per medium, cost from media_costs
Given a set of media options, determine which media should be selected so that all audiences are reached -> for each audience a: sum over media m with incidence[a][m] = 1 of is_selected[m] >= 1 (m.sum over the covering media, ">=", 1)
It does not matter if an audience is covered more than once, as long as it is covered at least once -> the >= 1 above, no upper bound
the company does not wish to spend more money on the campaign than necessary -> minimise total cost: scalar(is_selected, media_costs) = min_total_cost, setObjective MINIMIZE
Print is_selected as booleans and min_total_cost -> outputs is_selected = BoolVar[M], min_total_cost = IntVar total
