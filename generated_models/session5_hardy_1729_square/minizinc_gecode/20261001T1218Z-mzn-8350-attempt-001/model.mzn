% Hardy's 1729 with squares: find four different numbers a, b, c, d between 1 and
% 100 such that a^2 + b^2 = c^2 + d^2.
include "globals.mzn";

% the range of the numbers is fixed by the problem statement
int: range_min = 1;
int: range_max = 100;

var range_min..range_max: a;
var range_min..range_max: b;
var range_min..range_max: c;
var range_min..range_max: d;

% the sum of the squares of the first two numbers equals the sum of the squares of the other two
constraint a * a + b * b = c * c + d * d;

% the four numbers are all different
constraint all_different([a, b, c, d]);

solve satisfy;

output ["{\"a\": ", show(a), ", \"b\": ", show(b), ", \"c\": ", show(c), ", \"d\": ", show(d), "}"];
