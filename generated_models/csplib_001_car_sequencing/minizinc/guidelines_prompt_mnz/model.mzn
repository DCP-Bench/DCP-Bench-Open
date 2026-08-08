
include "globals.mzn";

% Input data
int: num_types = 6;
int: num_props = 5;
array[1..num_props] of int: at_most = [1, 2, 2, 2, 1];
array[1..num_props] of int: per_slots = [2, 3, 3, 5, 5];
array[1..num_types] of int: demand = [1, 1, 2, 2, 2, 2];
array[1..num_types, 1..num_props] of int: requires = 
  [| 1, 0, 1, 1, 0
   | 0, 0, 0, 1, 0
   | 0, 1, 0, 0, 1
   | 0, 1, 0, 1, 0
   | 1, 0, 1, 0, 0
   | 1, 1, 0, 0, 0 ];

int: total_cars = sum(i in 1..num_types)(demand[i]);

% Decision variable: sequence of cars (indexed 1..total_cars, values 1..num_types)
array[1..total_cars] of var 1..num_types: sequence;

% Ensure the exact demand for each car type
array[1..num_types] of var 0..total_cars: occ;
constraint
  forall(i in 1..num_types)(
    occ[i] = sum(p in 1..total_cars)(bool2int(sequence[p] == i))
  );
constraint
  forall(i in 1..num_types)(
    occ[i] = demand[i]
  );

% Sequencing constraints: for each property, in every window of per_slots[j], 
% the number of cars requiring that property ≤ at_most[j]
constraint
  forall(j in 1..num_props, p in 1..total_cars - per_slots[j] + 1)(
    sum(k in p..p+per_slots[j]-1)( requires[sequence[k], j] ) <= at_most[j]
  );

solve satisfy;

output [
  "{",
  "\"sequence\": [" ++ join(",", [show(sequence[i] - 1) | i in 1..total_cars]) ++ "]",
  "}"
];
