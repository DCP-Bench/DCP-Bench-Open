include "globals.mzn";

% We have 12 positions on the clock, numbered 1 to 12.
% The numbers 1 to 12 must be arranged so that no triplet of adjacent numbers has a sum higher than 21.
% The first number must be 12.

int: n = 12;
set of int: Positions = 1..n;
set of int: Numbers = 1..n;

% Decision variables: x[i] is the number at position i on the clock
array[Positions] of var Numbers: x;

% Constraint: all numbers are distinct
constraint all_different(x);

% Constraint: the first number is 12
constraint x[1] = 12;

% For each position i, consider the triplet of adjacent numbers:
% positions i, i+1, i+2 modulo 12 (wrapping around)
% The sum of these three numbers must be <= 21
constraint
  forall(i in Positions) (
    let {
      var int: a = x[i],
      var int: b = x[if i+1 <= n then i+1 else i+1 - n],
      var int: c = x[if i+2 <= n then i+2 else i+2 - n]
    } in
    a + b + c <= 21
  );

% Objective: minimize the maximum sum of any triplet of adjacent numbers
% But the problem states that 21 is the smallest possible maximum sum,
% so we just satisfy the constraints with max sum <= 21.

solve satisfy;

output [
  "{",
  "\"x\": ", show(x),
  "}"
];