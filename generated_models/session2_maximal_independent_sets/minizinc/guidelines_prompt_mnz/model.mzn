
% Number of nodes
int: n = 8;

% Adjacency list as a set for each node
array[1..n] of set of int: adjacency_list = [
    {2, 3, 7},
    {1, 4, 8},
    {1, 4, 5},
    {2, 3, 6},
    {3, 6, 7},
    {4, 5, 8},
    {1, 5, 8},
    {2, 6, 7}
];

% Decision variable: 1 if node i is in the independent set, 0 otherwise
array[1..n] of var 0..1: nodes;

% Independence constraints: no two adjacent nodes can both be 1
constraint
  forall(i in 1..n, j in adjacency_list[i]) (
    nodes[i] + nodes[j] <= 1
  );

% Maximality constraints: for each node, either it is in the set
% or at least one of its neighbors is in the set
constraint
  forall(i in 1..n) (
    nodes[i] + sum([nodes[j] | j in adjacency_list[i]]) >= 1
  );

solve satisfy;

output [
  "{",
    "\"nodes\": [" ++
      join(",", [show(nodes[i]) | i in 1..n])
    ++ "]",
  "}"
];
