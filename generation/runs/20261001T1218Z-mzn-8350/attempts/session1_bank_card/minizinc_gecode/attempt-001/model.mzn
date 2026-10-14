% Bank card: find the four digit PIN abcd from two facts about its two digit
% parts and from all four digits being different.
include "globals.mzn";

% the four digits of the PIN
var 0..9: a;
var 0..9: b;
var 0..9: c;
var 0..9: d;

% no two digits are the same
constraint all_different([a, b, c, d]);

% the 2-digit number cd is 3 times the 2-digit number ab
constraint 10 * c + d = 3 * (10 * a + b);

% the 2-digit number da is 2 times the 2-digit number bc
constraint 10 * d + a = 2 * (10 * b + c);

solve satisfy;

output ["{\"a\": ", show(a), ", \"b\": ", show(b), ", \"c\": ", show(c), ", \"d\": ", show(d), "}"];
