% Graceful graph: label the nodes of a graph with m edges with distinct numbers
% from 0..m so that the differences across the edges are all distinct.
include "globals.mzn";

int: m;  % number of edges
int: n;  % number of nodes
array[int, int] of int: graph;  % the edges, as pairs of node numbers counted from 0

% nodes[v] = label of node v (node numbers start at 0 in the data, so node v is
% position v + 1 here), taken from 0..m
array[1..n] of var 0..m: nodes;
% edges[e] = label of edge e, the absolute difference of its end labels; the
% differences of m distinct edges lie in 1..m
array[1..m] of var 1..m: edges;

% each edge is labelled with the absolute difference of the labels of its ends
constraint forall(e in 1..m) (edges[e] = abs(nodes[graph[e, 1] + 1] - nodes[graph[e, 2] + 1]));

% all edge labels are different
constraint all_different(edges);
% all node labels are different
constraint all_different(nodes);

solve satisfy;

output ["{\"nodes\": [", join(", ", [show(nodes[v]) | v in 1..n]),
        "], \"edges\": [", join(", ", [show(edges[e]) | e in 1..m]), "]}"];
