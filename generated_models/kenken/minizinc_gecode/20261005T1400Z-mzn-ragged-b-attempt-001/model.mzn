% KenKen: fill an n x n grid with 1..n so that every row and column holds each
% digit once and every cage reaches its target with +, -, x or /.
include "globals.mzn";

int: n;                                   % size of the grid
int: num_p;                               % number of cages
% each cage is [target, [cells]]; the runner binds the mixed row as one array
% per column: problem_1 the targets, problem_2 the cells padded to the
% largest cage, problem_2_len the real number of cells in each cage
array[int] of int: problem_1;
array[int,int,int] of int: problem_2;     % cage, cell, 1 = row / 2 = column (1-based)
array[int] of int: problem_2_len;

set of int: Cage = index_set(problem_1);
array[1..n, 1..n] of var 1..n: x;

% all rows and columns must be unique
constraint forall(i in 1..n)(all_different([x[i, j] | j in 1..n]));
constraint forall(j in 1..n)(all_different([x[i, j] | i in 1..n]));

% a two-cell cage reaches its target by sum, product, quotient (either way)
% or difference (either way)
constraint forall(c in Cage where problem_2_len[c] = 2)(
  let {
    var int: a = x[problem_2[c, 1, 1], problem_2[c, 1, 2]];
    var int: b = x[problem_2[c, 2, 1], problem_2[c, 2, 2]];
    int: res = problem_1[c];
  } in
    a + b = res \/ a * b = res \/ a * res = b \/ b * res = a
    \/ a - b = res \/ b - a = res
);

% any other cage reaches its target either as the sum or as the product of
% its cells; only the first problem_2_len[c] cells are real, the rest is padding
constraint forall(c in Cage where problem_2_len[c] != 2)(
  let {
    array[int] of var int: cells =
      [x[problem_2[c, k, 1], problem_2[c, k, 2]] | k in 1..problem_2_len[c]];
  } in
    sum(cells) = problem_1[c] \/ product(cells) = problem_1[c]
);

solve satisfy;

output ["{\"x\": [", join(", ", ["[" ++ join(", ", [show(x[i, j]) | j in 1..n]) ++ "]" | i in 1..n]), "]}"];
