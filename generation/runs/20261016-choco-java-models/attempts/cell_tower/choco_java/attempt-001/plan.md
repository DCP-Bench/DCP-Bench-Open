Problem: choose which potential cell tower sites to build, under a budget, to maximise the population covered; a region is covered when a built site reaches it.
Build decision per site -> build[s] BoolVar for each site s (count from the cost array)
Only limited towers within the budget: sum of cost_s * build_s <= budget -> m.scalar(build, cost, "<=", budget)
Region is covered when a built site covers it: covered_r = 1 iff some site with delta[s][r] = 1 is built -> covered_r <= sum of build_s over covering sites; build_s <= covered_r for each covering site
A region no site covers is never covered -> covered_r = 0
Maximise total population covered -> total = sum of population_r * covered_r; setObjective MAXIMIZE on total
