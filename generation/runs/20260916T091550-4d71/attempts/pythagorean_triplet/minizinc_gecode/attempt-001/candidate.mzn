% Pythagorean triplet: the one whose three members sum to 1000.
% The puzzle states its own total, so there are no parameters.
include "globals.mzn";

var 1..500: a;
var 1..500: b;
var 1..500: c;

constraint a + b + c = 1000;
constraint a * a + b * b = c * c;

solve satisfy;

output ["{\"a\": ", show(a), ", \"b\": ", show(b), ", \"c\": ", show(c), "}"];
