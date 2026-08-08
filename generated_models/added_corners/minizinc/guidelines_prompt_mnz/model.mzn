
% Include necessary library for global constraints
include "globals.mzn";

% Decision variables: four circles C1–C4 and four squares F1–F4
var 1..8: C1;
var 1..8: C2;
var 1..8: C3;
var 1..8: C4;
var 1..8: F1;
var 1..8: F2;
var 1..8: F3;
var 1..8: F4;

% All positions must be a permutation of 1..8
constraint all_different([C1,C2,C3,C4,F1,F2,F3,F4]);

% Each square equals the sum of its adjoining circles:
% F1 at (1,2) touches C1 (1,1) and C2 (1,3)
constraint F1 = C1 + C2;
% F2 at (2,1) touches C1 (1,1) and C3 (3,1)
constraint F2 = C1 + C3;
% F3 at (2,3) touches C2 (1,3) and C4 (3,3)
constraint F3 = C2 + C4;
% F4 at (3,2) touches C3 (3,1) and C4 (3,3)
constraint F4 = C3 + C4;

solve satisfy;

% Output the 3x3 grid (with 0 in the center) as JSON under key "positions"
output [
  "{",
  "\"positions\": [",
    "[", show(C1), ",", show(F1), ",", show(C2), "],",
    "[", show(F2), ",0,",        show(F3), "],",
    "[", show(C3), ",", show(F4), ",", show(C4), "]",
  "]",
  "}"
];
