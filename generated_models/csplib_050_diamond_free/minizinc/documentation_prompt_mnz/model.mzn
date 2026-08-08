include "globals.mzn";

% Number of vertices
int: N = 10;

% Possible degrees: positive multiples of 3 up to N-1 (max degree in simple graph)
set of int: DEG_VALUES = {d | d in 3..N-1 where d mod 3 = 0};

% Decision variables
array[1..N] of var DEG_VALUES: degree_seq;

% Adjacency matrix variables: 0/1 matrix, symmetric, no loops
array[1..N, 1..N] of var 0..1: adj;

% Constraints

% 1) Degree sequence is non-increasing
constraint forall(i in 1..N-1) (
    degree_seq[i] >= degree_seq[i+1]
);

% 2) Degree of each vertex is > 0 and multiple of 3 (already ensured by domain DEG_VALUES)

% 3) Sum of degrees is divisible by 12
constraint sum(i in 1..N)(degree_seq[i]) mod 12 = 0;

% 4) Adjacency matrix properties: symmetric, no loops
constraint forall(i in 1..N) (
    adj[i,i] = 0
);
constraint forall(i,j in 1..N where i < j) (
    adj[i,j] = adj[j,i]
);

% 5) Degree sequence matches adjacency matrix degrees
constraint forall(i in 1..N) (
    degree_seq[i] = sum(j in 1..N)(adj[i,j])
);

% 6) Diamond-free constraint:
% For every set of 4 distinct vertices, the number of edges among them is at most 4
% The number of edges among 4 vertices is sum of adj[u,v] for all pairs u<v in the 4 vertices
set of int: VERTICES = 1..N;
array[int] of var int: four_vertices = [0,0,0,0]; % placeholder for comprehension

% We use a forall over all 4-combinations of vertices
% For each combination, sum edges between them <= 4
constraint forall(vs in combinations(VERTICES,4)) (
    let {
        array[1..6] of var 0..1: edges_between = [
            adj[vs[1], vs[2]], adj[vs[1], vs[3]], adj[vs[1], vs[4]],
            adj[vs[2], vs[3]], adj[vs[2], vs[4]], adj[vs[3], vs[4]]
        ]
    } in
    sum(i in 1..6)(edges_between[i]) <= 4
);

% Solve: find all solutions
solve satisfy;

% Output adjacency matrix as "matrix"
output [
    "{",
    "\"matrix\": [",
    concat([
        "[" ++ join(",", [show(adj[i,j]) | j in 1..N]) ++ "]" ++ if i < N then "," else "" endif
        | i in 1..N
    ]),
    "]",
    "}"
];