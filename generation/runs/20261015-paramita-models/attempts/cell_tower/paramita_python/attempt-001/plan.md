# cell_tower plan (attempt-001)

- build a set of cell towers at the potential locations -> one Bool per site, build_tower[i]
- only a limited number can be built, within the budget -> sum(cost[i] * build_tower[i]) <= budget
- a region is covered when a built tower reaches it -> covered_r Iff Or(build_tower[i] for sites i reaching r)
- population covered by the built towers, maximised -> maximize sum(population[r] * covered_r)
- objective: maximize the total population covered (same expression as the output total_population_covered)
