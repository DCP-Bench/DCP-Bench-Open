
include "globals.mzn";

% Input data
int: num_tasks = 4;
int: num_people = 5;
array[1..num_tasks, 1..num_people] of int: cost = 
    [| 14, 5, 8, 7, 15
     | 2, 12, 6, 5, 3
     | 7, 8, 3, 9, 7
     | 2, 4, 6, 10, 1 |];

% Decision variables: x[t,p] = 1 if task t is assigned to person p
array[1..num_tasks, 1..num_people] of var 0..1: x;

% Constraint: each task is assigned to exactly one person
constraint
    forall(t in 1..num_tasks)(
        sum(p in 1..num_people)(x[t,p]) == 1
    );

% Objective: minimize total assignment cost
var int: total_cost = 
    sum(t in 1..num_tasks, p in 1..num_people)(cost[t,p] * x[t,p]);

solve minimize total_cost;

output [
    "{",
    "\"x\": [",
      join(",",
        [ "[" ++ join(",", [ show(x[t,p]) | p in 1..num_people ]) ++ "]"
          | t in 1..num_tasks ]
      ),
    "]",
    "}"
];
