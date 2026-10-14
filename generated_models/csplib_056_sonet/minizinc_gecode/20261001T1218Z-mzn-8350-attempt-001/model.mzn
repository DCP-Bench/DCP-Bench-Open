% SONET ring design: nodes are connected by rings and a node is put on a ring
% with one add-drop multiplexer (ADM). Two nodes that exchange traffic must share
% a ring, each ring holds a limited number of nodes, and the total number of
% ADMs, i.e. the total number of node-on-ring placements, is to be minimised.
include "globals.mzn";

int: r;                                 % maximum number of rings
int: n;                                 % number of nodes
array[1..n, 1..n] of int: demand;       % traffic between each pair of nodes
array[1..r] of int: capacity_nodes;     % most nodes each ring can hold

set of int: Rings = 1..r;
set of int: Nodes = 1..n;

% ring_config[k, i] = true if node i is on ring k
array[Rings, Nodes] of var bool: ring_config;

% every pair of nodes with traffic between them shares at least one ring
constraint forall(i in Nodes, j in Nodes where i < j /\ demand[i, j] > 0)
    (sum(k in Rings) (bool2int(ring_config[k, i] /\ ring_config[k, j])) >= 1);

% a ring holds at most its capacity of nodes
constraint forall(k in Rings) (sum(i in Nodes) (bool2int(ring_config[k, i])) <= capacity_nodes[k]);

% one ADM is used for each node placed on a ring; the total is to be minimised
var int: total_adms = sum(k in Rings, i in Nodes) (bool2int(ring_config[k, i]));
var int: objective = total_adms;
solve minimize objective;

output ["{\"ring_config\": [",
        join(", ", ["[" ++ join(", ", [show(ring_config[k, i]) | i in Nodes]) ++ "]" | k in Rings]),
        "], \"total_adms\": ", show(total_adms), "}"];
