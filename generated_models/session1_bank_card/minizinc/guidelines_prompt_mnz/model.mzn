
% Include global constraint library
include "globals.mzn";

% Decision variables: each digit 1..9 to ensure two-digit numbers have nonzero tens place
var 1..9: a;
var 1..9: b;
var 1..9: c;
var 1..9: d;

% All digits must be distinct
constraint all_different([a, b, c, d]);

% The 2-digit number cd is 3 times ab
constraint 10 * c + d == 3 * (10 * a + b);

% The 2-digit number da is 2 times bc
constraint 10 * d + a == 2 * (10 * b + c);

solve satisfy;

% Output the PIN as JSON
output [
  "{",
    join(",", [
      "\"a\": " ++ show(a),
      "\"b\": " ++ show(b),
      "\"c\": " ++ show(c),
      "\"d\": " ++ show(d)
    ]),
  "}"
];
