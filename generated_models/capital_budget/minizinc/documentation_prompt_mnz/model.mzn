% Stockco investment problem to maximize NPV given budget constraints

% Data
int: num_investments = 4;
array[1..num_investments] of int: npv = [16000, 22000, 12000, 8000];
array[1..num_investments] of int: cost = [5000, 7000, 4000, 3000];
int: budget = 14000;

% Decision variables: x[i] = 1 if investment i is chosen, 0 otherwise
array[1..num_investments] of var 0..1: x;

% Constraint: total cost must not exceed budget
constraint sum(i in 1..num_investments)(cost[i] * x[i]) <= budget;

% Objective: maximize total NPV
var int: total_npv = sum(i in 1..num_investments)(npv[i] * x[i]);
solve maximize total_npv;

output [
    "{",
    "\"x\": ", show(x),
    "}"
];