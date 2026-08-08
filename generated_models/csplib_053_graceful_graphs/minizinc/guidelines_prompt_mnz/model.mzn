
% Include necessary global constraints library
include "globals.mzn";

% Input data
int: m = 16;  % Number of edges
int: n = 8;   % Number of nodes
array[1..m, 1..2] of int: graph = array2d(1..m, 1..2, [
    0,1,  0,2,  0,3,  1,2,  1,3,  2,3,
    4,5,  4,6,  4,7,  5,6,  5,7,  6,7,
    0,4,  1,5,  2,6,  3,7
]);

% Decision variables
% nodes[i] is the label assigned to node i-1, in 0..m
array[1..n] of var 0..m: nodes;

% edges[k] is the absolute difference of labels on the k-th edge, in 1..m
array[1..m] of var 1..m: edges;

% Constraints
% All node labels must be different (0..m)
constraint all_different(nodes);

% Compute each edge label and enforce all are different
constraint
  forall(k in 1..m) (
    let {
      int: u = graph[k,1] + 1,  % convert to 1-based index
      int: v = graph[k,2] + 1
    } in
      edges[k] = abs(nodes[u] - nodes[v])
  )
  /\ all_different(edges);

% We only need to find any graceful labeling
solve satisfy;

% Output the node labels and edge labels in JSON format
output [
  "{",
    "\"nodes\": [" ++ join(",", [ show(nodes[i]) | i in 1..n ]) ++ "],",
    "\"edges\": [" ++ join(",", [ show(edges[k]) | k in 1..m ]) ++ "]",
  "}"
];
