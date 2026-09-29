% Devil's word: put a plus or minus sign in front of every number of a list so
% that the signed numbers add up to the given total.
include "globals.mzn";

array[int] of int: arr;  % the numbers, in order
int: total;              % the sum the signed numbers must reach

set of int: Positions = index_set(arr);

% plus[i] is true when arr[i] is added and false when it is subtracted
array[Positions] of var bool: plus;
% result[i] = arr[i] with its chosen sign
array[Positions] of var -max(arr)..max(arr): result;
constraint forall(i in Positions) (result[i] = if plus[i] then arr[i] else -arr[i] endif);

% the signed numbers add up to the total
constraint sum(result) = total;

% Implied by the line above, and stated so Gecode can prune: the numbers that
% are added weigh (total + sum(arr)) / 2 together, which also shows at once
% that the total must have the parity of sum(arr).
constraint 2 * sum(i in Positions) (arr[i] * bool2int(plus[i])) = total + sum(arr);

solve satisfy;

output ["{\"result\": [", join(", ", [show(result[i]) | i in Positions]), "]}"];
