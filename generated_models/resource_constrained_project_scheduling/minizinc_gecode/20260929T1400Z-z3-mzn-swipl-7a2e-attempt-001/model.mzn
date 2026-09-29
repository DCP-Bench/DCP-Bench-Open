% Resource-constrained project scheduling: start every job so that the
% precedence relations hold and, at every moment, the jobs running together use
% no more of each renewable resource than its capacity, finishing the project
% as early as possible.
include "globals.mzn";

array[int] of int: durations_data;
array[int, int] of int: resource_needs_data;   % needs[job, resource]
array[int] of int: resource_capacities_data;
array[int, int] of int: successors_link_data;  % [a, b]: job b starts after job a has finished, jobs counted from 0

set of int: Jobs = index_set(durations_data);
set of int: Resources = index_set(resource_capacities_data);
int: horizon = sum(durations_data);  % a schedule that runs one job at a time is never longer

% start_time[j] = when job j starts
array[Jobs] of var 0..horizon: start_time;

% a job can only start when its predecessor has finished (the data counts jobs from 0,
% job j is position j + 1 here)
constraint forall(k in index_set_1of2(successors_link_data)) (
    start_time[successors_link_data[k, 2] + 1]
        >= start_time[successors_link_data[k, 1] + 1] + durations_data[successors_link_data[k, 1] + 1]);

% at any time the jobs in progress need no more of a resource than is available
constraint forall(r in Resources) (
    cumulative(start_time, durations_data, [resource_needs_data[j, r] | j in Jobs], resource_capacities_data[r]));

% the project ends with its latest starting job (the last job is a zero-length
% dummy), so minimise the largest start time
var int: objective = max(start_time);
solve minimize objective;

output ["{\"start_time\": [", join(", ", [show(start_time[j]) | j in Jobs]), "]}"];
