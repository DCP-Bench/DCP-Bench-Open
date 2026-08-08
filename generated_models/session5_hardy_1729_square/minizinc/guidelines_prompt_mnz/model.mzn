
include "globals.mzn";

% Decision variables: four different integers between 1 and 100
var 1..100: a;
var 1..100: b;
var 1..100: c;
var 1..100: d;

% All four numbers must be distinct
constraint all_different([a, b, c, d]);

% Sum of squares constraint
constraint a*a + b*b = c*c + d*d;

solve satisfy;

% Output in JSON format with keys exactly as "a", "b", "c", "d"
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
