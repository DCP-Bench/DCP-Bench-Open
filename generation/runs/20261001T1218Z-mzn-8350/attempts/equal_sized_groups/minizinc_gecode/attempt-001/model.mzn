% Equal-sized groups: cut a sorted list of n values into k groups by choosing
% k - 1 break points, so that equal values stay in the same group and the group
% sizes are as close as possible to the ideal size round(n / k).
include "globals.mzn";

array[int] of int: a;  % the sorted list of values to divide
int: k;                % number of groups

int: n = length(a);

% ideal group size: n / k rounded the way Python's round() does it, which sends
% an exact half to the even integer (the reference rounds with round())
int: quotient = n div k;
int: twice_remainder = 2 * (n mod k);
int: gsize =
    if twice_remainder < k then quotient
    elseif twice_remainder > k then quotient + 1
    elseif quotient mod 2 = 0 then quotient
    else quotient + 1 endif;

% s[i] = number of elements in group i
array[1..k] of var 1..n: s;

% x[i] = break point i: the number of elements before the cut, i.e. the
% 1-based index of the last element of group i
array[1..k - 1] of var 1..n: x;

% z = total error: how far the group sizes are from the ideal size, to be minimised
var 0..n * k: z;
constraint z = sum(i in 1..k) (abs(s[i] - gsize));

% the first group ends at the first break point
constraint s[1] = x[1];

% the size of each middle group is the difference between its two break points
constraint forall(i in 2..k - 1) (s[i] = x[i] - x[i - 1]);

% the last group is what remains after the last break point
constraint s[k] = n - x[k - 1];

% Equal values must be in the same group: a cut right after position j would
% separate a[j] from a[j + 1], so it is only allowed where these differ
% (a cut after the last position is allowed by this rule and ruled out by
% the group sizes). Stated as a domain on x, which propagates better than one
% condition per position and is the same rule.
constraint forall(p in 1..k - 1) (x[p] in {j | j in 1..n where if j = n then true else a[j] != a[j + 1] endif});

var int: objective = z;
solve minimize objective;

output ["{\"x\": [", join(", ", [show(x[p]) | p in 1..k - 1]), "]}"];
