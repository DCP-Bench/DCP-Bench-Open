
include "globals.mzn";

% Input data
int: num_people = 8;
array[1..num_people] of array[int] of int: compatible = [
    [2, 3],
    [1, 6],
    [1, 4, 7],
    [2],
    [2],
    [5],
    [8],
    [3]
];

% Decision variables: transplants[i,j] = 1 if i donates to j, else 0
array[1..num_people, 1..num_people] of var 0..1: transplants;

% Compatibility constraint: only allow a transplant if compatible
constraint
  forall(i in 1..num_people, j in 1..num_people where not (j in compatible[i])) (
    transplants[i,j] = 0
  );

% Each person gives at most one kidney, receives at most one kidney,
% and must give iff they receive (row_sum = col_sum)
constraint
  forall(i in 1..num_people) (
    let {
      var int: out_i = sum(j in 1..num_people)(transplants[i,j]),
      var int: in_i  = sum(j in 1..num_people)(transplants[j,i])
    } in
      out_i <= 1 /\
      in_i <= 1 /\
      out_i = in_i
  );

% Objective: maximize the total number of transplants
solve maximize sum(i,j in 1..num_people)(transplants[i,j]);

% Output in JSON format
output [
    "{",
    "\"transplants\": [" ++
      join(",",
        [ "[" ++ join(",", [ show(transplants[i,j]) | j in 1..num_people ]) ++ "]"
          | i in 1..num_people
        ]
      ) ++ "]",
    "}"
];
