# cell_tower
Instance: `delta` (site x region coverage), `cost`, `population`, `budget`.
Outputs: `build_tower` (0/1 per site) and `total_population_covered`, which the
reference declares as the objective expression sum(population * covered).
Maximize covered population within the budget; a region counts as covered only
if one of its sites is built.
