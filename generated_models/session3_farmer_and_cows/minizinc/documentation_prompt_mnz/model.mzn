include "globals.mzn";

% Number of cows and sons
int: num_cows = 25;
int: num_sons = 5;

% Milk production per cow (cow i produces i kg)
array[1..num_cows] of int: milk = [i | i in 1..num_cows];

% Number of cows per son
array[0..num_sons-1] of int: cows_per_son = [7, 6, 5, 4, 3];

% Decision variables: assignment of each cow to a son (0..4)
array[1..num_cows] of var 0..num_sons-1: cow_assignments;

% Constraints

% 1) Each son gets exactly the specified number of cows
constraint
  forall(s in 0..num_sons-1) (
    sum([bool2int(cow_assignments[c] == s) | c in 1..num_cows]) == cows_per_son[s]
  );

% 2) The total milk produced by cows assigned to each son is the same
array[0..num_sons-1] of var int: milk_per_son;
constraint
  forall(s in 0..num_sons-1) (
    milk_per_son[s] = sum([milk[c] * bool2int(cow_assignments[c] == s) | c in 1..num_cows])
  );
constraint
  forall(s in 1..num_sons-1) (
    milk_per_son[s] == milk_per_son[0]
  );

solve satisfy;

output [
  "{",
  "\"cow_assignments\": ", show(cow_assignments),
  "}"
];