include "globals.mzn";

% Input data
int: num_jobs = 12;
array[1..num_jobs] of int: durations = [0, 3, 2, 5, 4, 2, 3, 4, 2, 4, 6, 0];
int: num_resources = 2;
array[1..num_jobs, 1..num_resources] of int: resource_needs = 
  [| 0, 0,
     5, 1,
     0, 4,
     1, 4,
     1, 3,
     3, 2,
     3, 1,
     2, 4,
     4, 0,
     5, 2,
     2, 5,
     0, 0 |];
array[1..num_resources] of int: resource_capacities = [6, 8];

int: num_successors = 18;
array[1..num_successors, 1..2] of int: successors_link = 
  [| 0, 1,
     0, 2,
     0, 3,
     1, 4,
     1, 5,
     2, 9,
     2, 10,
     3, 8,
     4, 6,
     4, 7,
     5, 9,
     5, 10,
     6, 8,
     6, 9,
     7, 8,
     8, 11,
     9, 11,
     10, 11 |];

% Adjust indices to 1-based for Minizinc arrays
% The input uses 0-based job indices, so add 1 to each
array[1..num_successors, 1..2] of int: successors = 
  [| successors_link[i,1] + 1, successors_link[i,2] + 1 | i in 1..num_successors];

% Calculate an upper bound for the schedule horizon as sum of all durations
int: horizon = sum(durations);

% Decision variables
array[1..num_jobs] of var 0..horizon: start_time;

% Calculate end times for convenience
array[1..num_jobs] of var 0..horizon: end_time = [start_time[j] + durations[j] | j in 1..num_jobs];

% Makespan variable to minimize
var 0..horizon: makespan;

% Constraints

% Precedence constraints: successor must start after predecessor finishes
constraint
  forall(s in 1..num_successors) (
    start_time[successors[s,2]] >= end_time[successors[s,1]]
  );

% Makespan is at least the end time of every job
constraint
  forall(j in 1..num_jobs) (
    makespan >= end_time[j]
  );

% Resource constraints: at any time, total resource usage <= capacity
% We use cumulative constraints for each resource
% For each resource, create arrays of start times, durations, and resource usage
constraint
  forall(r in 1..num_resources) (
    cumulative(
      start_time,
      durations,
      [resource_needs[j,r] | j in 1..num_jobs],
      resource_capacities[r]
    )
  );

% Solve to minimize makespan
solve minimize makespan;

output [
  "{",
  "\"start_time\": ", show(start_time),
  "}"
];