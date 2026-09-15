include "globals.mzn";

array[int, int] of int: delta;
array[int] of int: cost;
array[int] of int: population;
int: budget;

set of int: Sites = index_set(cost);
set of int: Regions = index_set(population);
array[Sites] of var bool: build_tower;
array[Regions] of var bool: covered;

% A region is covered exactly when one of its sites is built. The reference
% bounds this from one side only; stated that way, MiniZinc 2.9.3 flattens the
% budget constraint onto the wrong variable and leaves a tower unconstrained.
constraint forall(j in Regions) (
    covered[j] <-> exists(i in Sites) (delta[i, j] = 1 /\ build_tower[i]));
constraint sum(i in Sites) (cost[i] * bool2int(build_tower[i])) <= budget;

var int: objective = sum(j in Regions) (population[j] * bool2int(covered[j]));
solve maximize objective;

output ["{\"build_tower\": [", join(", ", [show(build_tower[i]) | i in Sites]),
        "], \"total_population_covered\": ", show(objective), "}"];
