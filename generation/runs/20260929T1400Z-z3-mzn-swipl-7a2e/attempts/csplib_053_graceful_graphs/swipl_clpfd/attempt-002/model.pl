:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Graceful graph: label the nodes of a graph with m edges with distinct numbers
% from 0..m so that the differences across the edges are all distinct.
model(Instance, Vars, [nodes-Nodes, edges-Edges]) :-
    M = Instance.m,          % number of edges
    N = Instance.n,          % number of nodes
    Graph = Instance.graph,  % the edges, as pairs of node numbers counted from 0

    % Nodes[v] = label of node v, taken from 0..m
    length(Nodes, N),
    Nodes ins 0..M,
    % Edges[e] = label of edge e, the absolute difference of its end labels; the
    % differences of m distinct edges lie in 1..m
    length(Edges, M),
    Edges ins 1..M,

    % each edge is labelled with the absolute difference of the labels of its ends
    maplist({Nodes}/[[U, V], Label]>>(nth0(U, Nodes, LabelU), nth0(V, Nodes, LabelV),
                                      Label #= abs(LabelU - LabelV)), Graph, Edges),

    % all edge labels are different
    all_distinct(Edges),
    % all node labels are different
    all_distinct(Nodes),
    append(Nodes, Edges, Vars).

% Label the node labels first, in order: the edge labels then follow from them.
% Choosing the variable with the smallest domain finds no solution in the budget.
labeling_options([leftmost]).
