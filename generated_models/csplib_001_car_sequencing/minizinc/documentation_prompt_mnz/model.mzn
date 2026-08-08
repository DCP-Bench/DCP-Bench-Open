include "globals.mzn";

% Input data
int: num_options = 5;
int: num_types = 6;
array[1..num_options] of int: at_most = [1, 2, 2, 2, 1];
array[1..num_options] of int: per_slots = [2, 3, 3, 5, 5];
array[1..num_types] of int: demand = [1, 1, 2, 2, 2, 2];
array[1..num_types, 1..num_options] of int: requires = 
  [| 1, 0, 1, 1, 0,
     0, 0, 0, 1, 0,
     0, 1, 0, 0, 1,
     0, 1, 0, 1, 0,
     1, 0, 1, 0, 0,
     1, 1, 0, 0, 0 |];

int: num_cars = sum(demand);

% Decision variable: sequence of car types on the assembly line
array[1..num_cars] of var 0..num_types-1: sequence;

% Constraint: demand fulfillment - each car type appears exactly demand times
constraint
  forall(t in 0..num_types-1) (
    count(sequence, t) == demand[t+1]
  );

% Constraint: capacity constraints for each option
% For each option, in every window of length per_slots[o], at most at_most[o] cars require that option
constraint
  forall(o in 1..num_options) (
    forall(i in 1..num_cars - per_slots[o] + 1) (
      sum([requires[sequence[j]+1, o] | j in i..i+per_slots[o]-1]) <= at_most[o]
    )
  );

solve satisfy;

output [
  "{",
  "\"sequence\": ", show(sequence),
  "}"
];