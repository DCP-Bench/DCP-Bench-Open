% Killer sudoku (CSPLib prob057): fill an n x n grid with 1..n so that every row,
% column and 3x3 nonet holds each number once, and the cells of every cage sum
% to the cage's number without repeating a value.
include "globals.mzn";

int: n;                                   % size of the grid
% problem rows are [sum, [cells]], each cell a 1-based [row, column]. The runner
% binds the two columns separately: problem_1 holds the sums, problem_2 the
% cells padded with [0, 0] to the largest cage, and problem_2_len the number of
% real cells in each cage.
array[int] of int: problem_1;
array[int,int,int] of int: problem_2;
array[int] of int: problem_2_len;

set of int: N = 1..n;
set of int: Cages = index_set(problem_1);
% the nonets are 3x3, as the reference fixes them
int: b = 3;

% x[r, c] = number in row r, column c
array[N, N] of var N: x;

% all rows and columns must be unique
constraint forall(r in N) (all_different([x[r, c] | c in N]));
constraint forall(c in N) (all_different([x[r, c] | r in N]));

% each nonet must be unique
constraint forall(i, j in 0..n div b - 1) (
    all_different([x[r, c] | r in i*b+1..i*b+b, c in j*b+1..j*b+b]));

% each cage's cells, read only up to the cage's length, sum to its number and
% hold different values
constraint forall(k in Cages) (
    let { array[int] of var int: cage =
              [x[problem_2[k, m, 1], problem_2[k, m, 2]] | m in 1..problem_2_len[k]] }
    in sum(cage) = problem_1[k] /\ all_different(cage));

solve satisfy;

output ["{\"x\": [", join(", ", ["[" ++ join(", ", [show(x[r, c]) | c in N]) ++ "]" | r in N]), "]}"];
