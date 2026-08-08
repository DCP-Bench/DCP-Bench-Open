
include "globals.mzn";

% Input Data
int: n = 12;  % number of jobs (including dummy start and end)
int: R = 2;   % number of resource types

array[1..n] of int: duration = 
    [0, 3, 2, 5, 4, 2, 3, 4, 2, 4, 6, 0];

array[1..n, 1..R] of int: resource_need = 
    array2d(1..n, 1..R,
        [ 0,0,  5,1,  0,4,  1,4,  1,3,  3,2,
          3,1,  2,4,  4,0,  5,2,  2,5,  0,0 ]
    );

array[1..R] of int: capacity = [6, 8];

% Precedence relations (converted from 0-based to 1-based indexing)
int: m = 18;
array[1..m, 1..2] of int: succ = array2d(1..m, 1..2,
    [ 1,2,  1,3,  1,4,  2,5,  2,6,  3,10,
      3,11, 4,9,  5,7,  5,8,  6,10, 6,11,
      7,9,  7,10, 8,9,  9,12,10,12,11,12 ]
);

% Compute a time horizon
int: horizon = sum(i in 1..n)(duration[i]);

% Decision variables
array[1..n] of var 0..horizon: start_time;
array[1..n] of var 0..horizon: end_time;

% Link start and end times
constraint
  forall(i in 1..n)(
    end_time[i] = start_time[i] + duration[i]
  );

% Precedence constraints
constraint
  forall(k in 1..m) (
    start_time[ succ[k,2] ] >= end_time[ succ[k,1] ]
  );

% Resource capacity constraints for each resource
constraint
  forall(r in 1..R) (
    cumulative(
      start_time,
      duration,
      [ resource_need[i,r] | i in 1..n ],
      capacity[r]
    )
  );

% Makespan variable and objective
var int: makespan;
constraint makespan = max(i in 1..n)(end_time[i]);

solve minimize makespan;

% Output start times in JSON
output [
  "{\"start_time\":[" ++
    join(",", [ show(start_time[i]) | i in 1..n ]) ++
  "]}"
];
