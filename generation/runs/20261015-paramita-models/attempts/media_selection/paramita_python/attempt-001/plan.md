The main media selection problem is a problem of allocating advertising budgets between possible advertising outlets. -> is_selected[m] Bool per medium (one-hot selection)
Given a set of media options, it aims to determine which media should be selected so that all audiences are reached with minimum campaign cost. -> minimise sum(media_costs[m] * is_selected[m])
It does not matter if an audience is covered more than once, as long as it is covered at least once. -> per audience a: sum(is_selected[m] for m covering a) >= 1 (incidence_matrix[a][m] == 1)
the company does not wish to spend more money on the campaign than necessary. -> objective minimise total cost
Print the binary decision of whether each media is selected (is_selected) as a list of booleans -> outputs is_selected as Bool list, length from advertising_media
and the total cost (min_total_cost). -> min_total_cost = same cost expression as the objective
Objective: minimise total campaign cost -> minimize sum(media_costs[m] * is_selected[m])
