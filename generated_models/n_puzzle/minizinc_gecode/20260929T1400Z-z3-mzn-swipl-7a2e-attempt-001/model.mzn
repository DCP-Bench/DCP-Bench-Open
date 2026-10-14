% N-puzzle (sliding tiles): list the board at each of N_STEPS steps, from the
% start state to the end state, where every step slides one tile into the empty
% square (0) and the board changes at each step.
include "globals.mzn";

int: N_STEPS;  % boards in the solution, start and end included
array[int, int] of int: puzzle_start;  % 0 marks the empty square
array[int, int] of int: puzzle_end;

int: dim = card(index_set_1of2(puzzle_start));
int: tiles = dim * dim - 1;  % e.g. 8 tiles for a 3 x 3 board

% steps[t, i, j] = the tile on square (i, j) at step t
array[1..N_STEPS, 1..dim, 1..dim] of var 0..tiles: steps;

% the first board is the start state and the last one the end state
constraint forall(i, j in 1..dim) (steps[1, i, j] = puzzle_start[i, j] /\ steps[N_STEPS, i, j] = puzzle_end[i, j]);

constraint forall(t in 2..N_STEPS) (
    % each board uses every tile once
    all_different([steps[t, i, j] | i, j in 1..dim]) /\
    forall(i, j in 1..dim) (
        % the empty square can only move to a neighbouring square: where it is empty
        % now it was empty here or on an adjacent square before
        (steps[t, i, j] = 0 -> exists(a, b in 1..dim where abs(a - i) + abs(b - j) <= 1) (steps[t - 1, a, b] = 0)) /\
        % only the empty square moves: a square that is neither empty before nor
        % empty after keeps its tile
        (steps[t - 1, i, j] = 0 \/ steps[t, i, j] = 0 \/ steps[t - 1, i, j] = steps[t, i, j])) /\
    % the board must change at every step (no standing still)
    exists(i, j in 1..dim) (steps[t - 1, i, j] != steps[t, i, j]));

solve satisfy;

output ["{\"steps\": [",
        join(", ", ["[" ++ join(", ", ["[" ++ join(", ", [show(steps[t, i, j]) | j in 1..dim]) ++ "]" | i in 1..dim]) ++ "]"
                    | t in 1..N_STEPS]), "]}"];
