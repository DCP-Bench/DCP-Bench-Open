% Graceful graphs (CSPLib 053).
% A labelling f of the nodes of a graph with q edges is graceful if f assigns
% each node a unique label from {0, 1, ..., q} and, when each edge xy is labelled
% with |f(x) - f(y)|, the edge labels are all different.
% Output: the node labels (nodes) and the edge labels (edges).

:- lib(ic).

model(Instance, Vars, [nodes-Nodes, edges-Edges]) :-
    memberchk(n-N, Instance),
    memberchk(m-M, Instance),
    memberchk(graph-G, Instance),
    length(Nodes, N),
    length(Edges, M),

    % each node gets a unique label from 0..q, q the number of edges
    Nodes :: 0..M,
    alldifferent(Nodes),

    % each edge xy is labelled with |f(x) - f(y)|, and the edge labels are all different
    (
        foreach(Pair, G),
        foreach(Ed, Edges),
        param(Nodes, M)
    do
        Pair = [A, B],
        A1 is A + 1,
        B1 is B + 1,
        element(A1, Nodes, Xa),
        element(B1, Nodes, Xb),
        Ed :: 1..M,
        Ed #= abs(Xa - Xb)
    ),
    alldifferent(Edges),

    Vars = Nodes.

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).
