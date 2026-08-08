include "globals.mzn";

% Guests indexed as:
% 0: Andrew
% 1: Betty
% 2: Cara
% 3: Dave
% 4: Erica
% 5: Frank

int: n = 6;

% Allowed neighbors for each guest (0-based indices)
array[0..n-1] of set of int: allowed_neighbors = [
    {3,5},    % Andrew only next to Dave(3) and Frank(5)
    {2,4},    % Betty only next to Cara(2) and Erica(4)
    {1,5},    % Cara only next to Betty(1) and Frank(5)
    {0,4},    % Dave only next to Andrew(0) and Erica(4)
    {1,3},    % Erica only next to Betty(1) and Dave(3)
    {0,2}     % Frank only next to Andrew(0) and Cara(2)
];

% Decision variable: seating order, array of guests in seat order 1..6
array[1..n] of var 0..n-1: x;

% All guests must be seated exactly once
constraint all_different(x);

% Function to get neighbors of seat i (circular table)
function array[int] of int: neighbors(int: i) =
    if i = 1 then [n, 2]
    elseif i = n then [n-1, 1]
    else [i-1, i+1]
    endif;

% Calculate conflicts: count number of adjacent pairs where guests do not get along
var 0..n*2: conflicts;

% We count conflicts by checking each pair of neighbors once
% To avoid double counting, only count pairs where seat i < seat j
array[1..n] of var 0..1: conflict_per_seat;

constraint
    forall(i in 1..n) (
        let {
            array[int] of int: nbrs = neighbors(i),
            var 0..1: seat_conflict = 
                max([bool2int(not (x[nbr] in allowed_neighbors[x[i]])) | nbr in nbrs])
        } in
            conflict_per_seat[i] = seat_conflict
    );

% Each conflict is counted twice (once per each seat in the pair), so total conflicts is half sum
constraint conflicts = sum(conflict_per_seat) div 2;

solve minimize conflicts;

output [
    "{",
    "\"x\": ", show(x),
    "}"
];