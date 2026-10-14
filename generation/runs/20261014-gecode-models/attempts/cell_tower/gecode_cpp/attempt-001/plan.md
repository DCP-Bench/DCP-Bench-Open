# Plan: cell_tower (maximise population covered under a build budget)

Problem: choose towers (sites) to build; a region is covered when a built tower reaches it; total cost of built towers <= budget; maximise total population of covered regions.

- build_tower[i] = 1 if a tower is built at site i -> BoolVarArray(*this, S, 0, 1), output build_tower.
- covered_r = 1 if region r is covered -> BoolVarArray(*this, R, 0, 1).
- a region is covered only if a tower covering it is built (a covered region needs a built tower in its coverage list) -> linear(*this, coef, bools, IRT_GQ, 0) over the covering sites (+1) and covered_r (-1), BOOL linear, no reification.
- the total cost of the built towers stays within the budget -> linear(*this, IntArgs(cost), build, IRT_LQ, budget).
- total population covered = sum over regions of population_r * covered_r -> linear(*this, IntArgs(population), covered, IRT_EQ, total) with total IntVar in 0..sum(population) (IntVar maximised).
- Branching: build_tower first (BOOL_VAR_NONE, BOOL_VAL_MAX), then covered (BOOL_VAR_NONE, BOOL_VAL_MAX).
- Objective: maximize(total).
- Sizes: S = number of sites = instance delta rows; R = number of regions = instance population length. Both read from the instance.
