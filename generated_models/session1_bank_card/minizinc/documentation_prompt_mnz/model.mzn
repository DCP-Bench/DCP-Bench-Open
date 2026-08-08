include "globals.mzn";

% Variables: digits of the PIN
var 0..9: a;
var 0..9: b;
var 0..9: c;
var 0..9: d;

% Constraints
constraint all_different([a,b,c,d]);

% The 2-digit number cd = 10*c + d
% The 2-digit number ab = 10*a + b
constraint 10*c + d = 3 * (10*a + b);

% The 2-digit number da = 10*d + a
% The 2-digit number bc = 10*b + c
constraint 10*d + a = 2 * (10*b + c);

% Solve for any solution satisfying the constraints
solve satisfy;

output [
    "{",
    "\"a\": ", show(a), ",",
    "\"b\": ", show(b), ",",
    "\"c\": ", show(c), ",",
    "\"d\": ", show(d),
    "}"
];