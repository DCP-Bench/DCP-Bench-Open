% Bus driver scheduling (CSPLib prob022): choose a subset of the possible shifts
% so that every piece of work is covered by exactly one chosen shift, using as
% few shifts as possible.
include "globals.mzn";

int: num_work;                            % pieces of work, numbered 0..num_work-1
int: num_shifts;                          % possible shifts
% shifts[i] lists the pieces of work shift i covers. Rows differ in length, so
% the runner pads them with 0, which is also a real piece of work: only the
% first shifts_len[i] entries of row i belong to shift i.
array[int,int] of int: shifts;
array[int] of int: shifts_len;

set of int: Shifts = 1..num_shifts;
set of int: Work = 0..num_work-1;

% the set of pieces of work each shift covers, read up to the row's length
array[Shifts] of set of int: covers = [{shifts[i, k] | k in 1..shifts_len[i]} | i in Shifts];

% x[i] = true if shift i is selected
array[Shifts] of var bool: x;

% each piece of work is covered by exactly one selected shift (set partitioning)
constraint forall(t in Work) (
    sum(i in Shifts where t in covers[i]) (bool2int(x[i])) = 1);

% implied by the partitioning: the chosen shifts together cover every piece of
% work once, so their sizes add up to num_work (counting only pieces in 0..num_work-1)
constraint sum(i in Shifts) (card(covers[i] intersect Work) * bool2int(x[i])) = num_work;

% minimise the number of shifts used
var int: objective = sum(i in Shifts) (bool2int(x[i]));
solve minimize objective;

output ["{\"x\": [", join(", ", [show(x[i]) | i in Shifts]), "]}"];
