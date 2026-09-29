% Aircraft landing with a fixed landing order: give every aircraft a landing
% time inside its window so that consecutive landings keep the required
% separation, minimising the penalty for landing before or after the target.
include "globals.mzn";

array[int] of int: earliest_landing;  % start of each aircraft's window
array[int] of int: latest_landing;    % end of each aircraft's window
array[int] of int: target_landing;    % preferred landing time
array[int] of int: penalty_before;    % cost per time unit landing early
array[int] of int: penalty_after;     % cost per time unit landing late
array[int, int] of int: separation_time;  % minimum gap between two landings

set of int: Aircraft = index_set(earliest_landing);
int: horizon = max(latest_landing);

array[Aircraft] of var 0..horizon: landing_times;
% how far before / after its target each aircraft lands
array[Aircraft] of var 0..horizon: earliness;
array[Aircraft] of var 0..horizon: lateness;

% each aircraft lands inside its time window
constraint forall(i in Aircraft) (landing_times[i] >= earliest_landing[i] /\ landing_times[i] <= latest_landing[i]);

% the deviation from the target is split into earliness and lateness; the
% positive penalties make the solver keep one of the two at zero
constraint forall(i in Aircraft) (landing_times[i] - target_landing[i] = lateness[i] - earliness[i]);

% the landing order is fixed as the aircraft index order (as the problem
% states), so aircraft j lands at least separation_time[i, j] after aircraft i
constraint forall(i, j in Aircraft where i < j) (landing_times[j] - landing_times[i] >= separation_time[i, j]);

% total penalty for early and late landings, to be minimised
var int: total_penalty = sum(i in Aircraft) (penalty_before[i] * earliness[i] + penalty_after[i] * lateness[i]);
var int: objective = total_penalty;
solve minimize objective;

output ["{\"landing_times\": [", join(", ", [show(landing_times[i]) | i in Aircraft]),
        "], \"total_penalty\": ", show(total_penalty), "}"];
