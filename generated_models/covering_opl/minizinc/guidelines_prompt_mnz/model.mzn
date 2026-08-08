
include "globals.mzn";

% Input data
int: nb_workers = 32;
int: num_tasks = 15;

array[1..num_tasks] of set of 1..nb_workers: Qualified = [
  {1, 9, 19, 22, 25, 28, 31},
  {2, 12, 15, 19, 21, 23, 27, 29, 30, 31, 32},
  {3, 10, 19, 24, 26, 30, 32},
  {4, 21, 25, 28, 32},
  {5, 11, 16, 22, 23, 27, 31},
  {6, 20, 24, 26, 30, 32},
  {7, 12, 17, 25, 30, 31},
  {8, 17, 20, 22, 23},
  {9, 13, 14, 26, 29, 30, 31},
  {10, 21, 25, 31, 32},
  {14, 15, 18, 23, 24, 27, 30, 32},
  {18, 19, 22, 24, 26, 29, 31},
  {11, 20, 25, 28, 30, 32},
  {16, 19, 23, 31},
  {9, 18, 26, 28, 31, 32}
];

array[1..nb_workers] of int: Cost = [
  1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 3,
  3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 6, 6, 6, 7, 8, 9
];

% Decision variables: whether to hire each worker
array[1..nb_workers] of var 0..1: workers;

% Total cost of hired workers
var int: total_cost = sum(w in 1..nb_workers)(workers[w] * Cost[w]);

% Each task must be covered by at least one qualified worker
constraint
  forall(t in 1..num_tasks) (
    sum(w in Qualified[t])(workers[w]) >= 1
  );

% Minimize the hiring cost
solve minimize total_cost;

% JSON output
output [
  "{",
    "\"total_cost\": " ++ show(total_cost) ++ ",",
    "\"workers\": [" ++ join(",", [ show(workers[w]) | w in 1..nb_workers ]) ++ "]",
  "}"
];
