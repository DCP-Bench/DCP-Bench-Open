include "globals.mzn";

% Decision variables: digits assigned to each letter
var 0..9: s;
var 0..9: e;
var 0..9: n;
var 0..9: d;
var 0..9: m;
var 0..9: o;
var 0..9: r;
var 0..9: y;

% All letters must have distinct digits
constraint alldifferent([s,e,n,d,m,o,r,y]);

% Leading letters cannot be zero
constraint s != 0;
constraint m != 0;

% SEND + MORE = MONEY
% Represent the words as numbers:
% SEND = 1000*s + 100*e + 10*n + d
% MORE = 1000*m + 100*o + 10*r + e
% MONEY = 10000*m + 1000*o + 100*n + 10*e + y

constraint 
  (1000*s + 100*e + 10*n + d) + (1000*m + 100*o + 10*r + e) = 
  (10000*m + 1000*o + 100*n + 10*e + y);

solve satisfy;

output [
  "{",
  join(",", [
    "\"s\": " ++ show(s),
    "\"e\": " ++ show(e),
    "\"n\": " ++ show(n),
    "\"d\": " ++ show(d),
    "\"m\": " ++ show(m),
    "\"o\": " ++ show(o),
    "\"r\": " ++ show(r),
    "\"y\": " ++ show(y)
  ]),
  "}"
];