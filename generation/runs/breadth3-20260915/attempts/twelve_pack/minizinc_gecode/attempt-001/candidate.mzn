include "globals.mzn";

int: target;
array[int] of int: packs;

set of int: Sizes = index_set(packs);
% The reference's own arbitrary ceiling on a pack count.
int: ceiling = target * 2;
array[Sizes] of var 0..ceiling: counts;
var 0..ceiling * length(packs): total;

constraint total = sum(i in Sizes) (counts[i] * packs[i]);
constraint total >= target;

var int: objective = total;
solve minimize objective;

output ["{\"counts\": [", join(", ", [show(counts[i]) | i in Sizes]), "]}"];
