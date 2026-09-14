include "globals.mzn";

int: N;

array[1..N, 1..N] of var bool: matrix;

% No isolated vertex, and every degree is a multiple of three.
constraint forall(i in 1..N) (
    sum(j in 1..N) (bool2int(matrix[i, j])) > 0
  /\ sum(j in 1..N) (bool2int(matrix[i, j])) mod 3 = 0
);
% The number of arcs is a multiple of twelve.
constraint sum(i, j in 1..N) (bool2int(matrix[i, j])) mod 12 = 0;
% No self loop, and the graph is undirected.
constraint forall(i in 1..N) (not matrix[i, i]);
constraint forall(i, j in 1..N where i < j) (matrix[i, j] = matrix[j, i]);
% Diamond-free: any four vertices span at most four of their six edges.
constraint forall(a, b, c, d in 1..N where a < b /\ b < c /\ c < d) (
    bool2int(matrix[a, b]) + bool2int(matrix[a, c]) + bool2int(matrix[a, d])
  + bool2int(matrix[b, c]) + bool2int(matrix[b, d]) + bool2int(matrix[c, d]) <= 4
);

solve satisfy;

output ["{\"matrix\": [",
        join(", ", ["[" ++ join(", ", [show(matrix[i, j]) | j in 1..N]) ++ "]" | i in 1..N]),
        "]}"];
