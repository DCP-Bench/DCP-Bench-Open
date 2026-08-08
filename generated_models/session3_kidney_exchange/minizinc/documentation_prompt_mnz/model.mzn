include "globals.mzn";

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

// Decision variables: transplants[i,j] = 1 if person i donates to person j, 0 otherwise
array[1..num_people, 1..num_people] of var 0..1: transplants;

// Constraint: transplants[i,j] can be 1 only if j is in compatible[i]
constraint
  forall(i in 1..num_people, j in 1..num_people) (
    transplants[i,j] = 1 -> (j in compatible[i])
  );

// Constraint: no person receives more than one kidney
constraint
  forall(j in 1..num_people) (
    sum(i in 1..num_people)(transplants[i,j]) <= 1
  );

// Constraint: anyone who gives a kidney must receive one
constraint
  forall(i in 1..num_people) (
    sum(j in 1..num_people)(transplants[i,j]) = sum(k in 1..num_people)(transplants[k,i])
  );

// Objective: maximize the number of people that receive a new kidney
var int: total_transplants = sum(i,j in 1..num_people)(transplants[i,j]);
solve maximize total_transplants;

output [
  "{",
  "\"transplants\": [",
  join(",\n", [
    "[" ++ join(", ", [show(transplants[i,j]) | j in 1..num_people]) ++ "]"
    | i in 1..num_people
  ]),
  "]",
  "}"
];