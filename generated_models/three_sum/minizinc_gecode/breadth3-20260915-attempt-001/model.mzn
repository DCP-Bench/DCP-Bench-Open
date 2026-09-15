include "globals.mzn";

array[int] of int: nums;
int: m;

set of int: Items = index_set(nums);
array[Items] of var bool: indices;

constraint sum(i in Items) (nums[i] * bool2int(indices[i])) = 0;
constraint sum(i in Items) (bool2int(indices[i])) = m;

solve satisfy;

output ["{\"indices\": [", join(", ", [show(indices[i]) | i in Items]), "]}"];
