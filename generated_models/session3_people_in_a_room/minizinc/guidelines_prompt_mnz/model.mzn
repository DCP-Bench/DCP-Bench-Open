
% Include globals for sum/forall
include "globals.mzn";

% Decision variable: 0 = male, 1 = female
array[1..13] of var 0..1: sequence;

% Exactly 9 females (and 4 males)
constraint sum(i in 1..13)(sequence[i]) = 9;

% At any prefix t, ratio females/males <= 7/3
% i.e., 3 * F_t <= 7 * M_t, where F_t = sum of sequence[1..t], M_t = t - F_t
constraint
  forall(t in 1..13) (
    3 * sum(i in 1..t)(sequence[i])
    <= 7 * (t - sum(i in 1..t)(sequence[i]))
  );

solve satisfy;

% Output result as JSON
output [
  "{",
  join(",", [
    "\"sequence\": [" ++ join(",", [ show(sequence[i]) | i in 1..13 ]) ++ "]"
  ]),
  "}"
];
