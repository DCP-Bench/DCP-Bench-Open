% Scheduling with a shared resource: five tasks, two workers. Task 1
% must finish before task 3 starts, and task 2 before task 4. Minimise
% the makespan (the finish time of the last task).
include "globals.mzn";

int: n = 5;
int: workers = 2;
array[1..n] of int: dur = [3, 2, 4, 2, 3];
array[1..n] of int: need = [1, 1, 2, 1, 1];

int: horizon = sum(dur);
array[1..n] of var 0..horizon: start;
var 0..horizon: makespan;

constraint cumulative(start, dur, need, workers);
constraint start[1] + dur[1] <= start[3];
constraint start[2] + dur[2] <= start[4];
constraint forall(i in 1..n)(start[i] + dur[i] <= makespan);

solve minimize makespan;

output ["start = ", show(start), "\n",
        "makespan = ", show(makespan), "\n"];
