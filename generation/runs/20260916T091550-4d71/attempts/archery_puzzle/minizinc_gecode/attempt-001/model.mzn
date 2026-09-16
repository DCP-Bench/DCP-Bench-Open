% Archery puzzle: fire as many arrows as you like at the given targets and land
% as close to the target score as possible.
include "globals.mzn";

array[int] of int: targets;
int: target_score;

set of int: Targets = index_set(targets);
array[Targets] of var 0..target_score: hits;
var 0..target_score * 2: score;
var 0..target_score * 2: deviation;

constraint score = sum(i in Targets) (targets[i] * hits[i]);
constraint deviation = abs(target_score - score);

var int: objective = deviation;
solve minimize objective;

output ["{\"hits\": [", join(", ", [show(hits[i]) | i in Targets]), "]}"];
