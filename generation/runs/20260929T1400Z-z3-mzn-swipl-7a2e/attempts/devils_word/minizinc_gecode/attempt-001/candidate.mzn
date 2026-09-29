% Devil's word: put a plus or minus sign in front of every number of a list so
% that the signed numbers add up to the given total.
include "globals.mzn";

array[int] of int: arr;  % the numbers, in order
int: total;              % the sum the signed numbers must reach

set of int: Positions = index_set(arr);

% result[i] = arr[i] with its chosen sign: either +arr[i] or -arr[i]
array[Positions] of var -max(arr)..max(arr): result;
constraint forall(i in Positions) (result[i] = arr[i] \/ result[i] = -arr[i]);

% the signed numbers add up to the total
constraint sum(result) = total;

solve satisfy;

output ["{\"result\": [", join(", ", [show(result[i]) | i in Positions]), "]}"];
