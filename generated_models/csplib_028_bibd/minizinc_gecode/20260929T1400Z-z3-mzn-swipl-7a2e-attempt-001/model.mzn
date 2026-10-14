% Balanced incomplete block design: arrange v objects into b blocks so that a
% block holds k objects, an object lies in r blocks, and any two distinct
% objects share exactly l blocks. Solved through the v x b incidence matrix.
include "globals.mzn";

int: v;
int: b;
int: r;
int: k;
int: l;

% matrix[i, j] is true when object i belongs to block j
array[1..v, 1..b] of var bool: matrix;

% every object occurs in exactly r blocks (each row adds up to r)
constraint forall(i in 1..v) (sum(j in 1..b) (bool2int(matrix[i, j])) = r);

% every block contains exactly k objects (each column adds up to k)
constraint forall(j in 1..b) (sum(i in 1..v) (bool2int(matrix[i, j])) = k);

% any two distinct objects occur together in exactly l blocks: the scalar
% product of their rows is l
constraint forall(i1, i2 in 1..v where i1 < i2) (
    sum(j in 1..b) (bool2int(matrix[i1, j] /\ matrix[i2, j])) = l);

solve satisfy;

output ["{\"matrix\": [",
        join(", ", ["[" ++ join(", ", [show(matrix[i, j]) | j in 1..b]) ++ "]" | i in 1..v]),
        "]}"];
