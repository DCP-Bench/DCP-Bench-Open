
include "globals.mzn";

/*
  Solve the puzzle:
  - A1, A2, A3 are ages (positive integers) sorted non-increasingly.
  - The product A1*A2*A3 = 36.
  - The sum windows = A1 + A2 + A3 is ambiguous among possible triplets,
    i.e., there are at least two distinct triples (B1,B2,B3) with the same sum
    and product = 36.
  - The oldest son is unique, so A1 > A2.
*/

% Decision variables: ages sorted descending
var 1..36: A1;
var 1..36: A2;
var 1..36: A3;

% Ensure non-increasing order
constraint A1 >= A2 /\ A2 >= A3;

% Product constraint
constraint A1 * A2 * A3 = 36;

% Sum (number of windows)
var int: windows = A1 + A2 + A3;

% Count how many (B1,B2,B3) meet the same product=36, sum=windows and sorted order
var int: count_solutions = 
  sum([ bool2int(
           B1*B2*B3 = 36
        /\ B1 + B2 + B3 = windows
        /\ B1 >= B2
        /\ B2 >= B3
      )
      | B1 in 1..36, B2 in 1..36, B3 in 1..36
  ]);

% Mathematician initially was unsure => more than one solution for the same sum
constraint count_solutions > 1;

% Oldest son is unique
constraint A1 > A2;

solve satisfy;

% Output in JSON format
output [
  "{",
  join(",", [
    "\"A1\": " ++ show(A1),
    "\"A2\": " ++ show(A2),
    "\"A3\": " ++ show(A3)
  ]),
  "}"
];
