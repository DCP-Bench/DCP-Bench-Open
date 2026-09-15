include "globals.mzn";

array[int, int] of int: delta;
array[int] of int: cost;
array[int] of int: population;
int: budget;

set of int: Sites = index_set(cost);
set of int: Regions = index_set(population);
array[Sites] of var bool: build_tower;
array[Regions] of var bool: covered;

constraint forall(j in Regions) (
    bool2int(covered[j]) <= sum(i in Sites) (delta[i, j] * bool2int(build_tower[i])));
constraint sum(i in Sites) (cost[i] * bool2int(build_tower[i])) <= budget;

var int: objective = sum(j in Regions) (population[j] * bool2int(covered[j]));
solve maximize objective;

output ["{\"build_tower\": [", join(", ", [show(build_tower[i]) | i in Sites]),
        "], \"total_population_covered\": ", show(objective), "}"];
